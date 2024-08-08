import getopt
import logging
import subprocess
import sys
import uuid
from random import randint
from time import sleep


def first_container_id(network='devnet', node_type='solo'):
    container_name = f'celestia-{node_type}-{network}'
    proc = subprocess.run(['docker', 'ps'], stdout=subprocess.PIPE)
    containers = dict((line.split()[-1], line.split()[0])
                      for line in proc.stdout.decode('utf8').split('\n')[1:] if line)
    for name, id in sorted(containers.items(), key=lambda x: x[0], reverse=True):
        if name.startswith(container_name):
            return id


def start_node(*args_, version='v0.14.0'):
    if args_:
        network, node_type, rpc_url = args_
        container_name = f'celestia-{node_type}-{network}-{uuid.uuid4()}'
        image = f'ghcr.io/celestiaorg/celestia-node:{version}'
        args = ['docker', 'run', '-e', f'NODE_TYPE={node_type}', '-e', f'P2P_NETWORK={network}',
                '--net=host', '--name', container_name, '-d', image,
                'celestia', node_type, 'start', '--core.ip', rpc_url, '--p2p.network', network]
    else:
        container_name = f'celestia-solo-devnet-{uuid.uuid4()}'
        image = 'ghcr.io/rollkit/local-celestia-devnet:latest'
        args = ['docker', 'run', '--net=host', '--name', container_name, '-d', image]
    proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode == 0:
        container_id = proc.stdout.decode('utf8').strip()
        return container_id[:12]
    logging.error(proc.stderr.decode('utf8'))
    assert proc.returncode == 0


def stop_node(network='devnet', node_type='solo'):
    container_id = first_container_id(network, node_type)
    if container_id:
        proc = subprocess.run(['docker', 'stop', container_id], stdout=subprocess.PIPE)
        assert proc.returncode == 0
        proc = subprocess.run(['docker', 'rm', container_id], stdout=subprocess.PIPE)
        assert proc.returncode == 0


def show_token(network='devnet', node_type='solo', permission='admin'):
    container_id = first_container_id(network, node_type)
    if not container_id:
        return ''
    args = ['docker', 'exec', '-i', container_id]
    if network == 'devnet':
        node_type = 'bridge'
        network = 'private'
        args = [*args, '--node.store', '/home/celestia/bridge']
    cnt = 10
    proc = None
    args = [*args[:4], 'celestia', node_type, 'auth', permission, '--p2p.network', network, *args[4:]]
    while cnt:
        proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode == 0:
            token = proc.stdout.decode('utf8').strip()
            return token
        sleep(1)
        cnt -= 1
    logging.error(proc.stderr.decode('utf8'))
    assert proc.returncode == 0


def command():
    cmd = sys.argv[0].split('/')[-1]
    rpc_urls = {
        'arabica': ['validator-1.celestia-arabica-11.com',
                    'validator-2.celestia-arabica-11.com',
                    'validator-3.celestia-arabica-11.com',
                    'validator-4.celestia-arabica-11.com'],
        'mocha': ['public-celestia-mocha4-consensus.numia.xyz',
                  'mocha-4-consensus.mesa.newmetric.xyz',
                  'full.consensus.mocha-4.celestia-mocha.com',
                  'consensus-full-mocha-4.celestia-mocha.com',
                  'rpc-mocha.pops.one']
    }
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["rpc-url"])
        if len(args) == 0:
            raise getopt.GetoptError('Invalid arguments')
    except getopt.GetoptError as err:
        print(err)
        print(f"Usage: {cmd} network [node-type] {'[--rpc-url URL]' if cmd == 'start-node' else ''}")
        sys.exit(2)

    args = args + ['light'] if len(args) == 1 else args
    network, node_type = ['devnet', 'solo'] if args[0] == 'devnet' else args

    match cmd:
        case 'start-node':
            if network == 'devnet':
                print(start_node())
            else:
                rpc_url = dict(opts).get('--rpc-url', rpc_urls[network][randint(0, len(rpc_urls[network]) - 1)])
                print(start_node(network, node_type, rpc_url))
        case 'stop-node':
            stop_node(network, node_type)
        case 'show-token':
            print(show_token(network, node_type))
