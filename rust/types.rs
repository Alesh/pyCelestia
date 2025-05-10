use celestia_types::nmt::{Namespace, NS_SIZE};
use celestia_types::state::{AccAddress, Address, AddressTrait};
use celestia_types::{AppVersion, Blob};
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{IntoPyDict, PyBytes, PyDict, PyString};
use pyo3::IntoPyObjectExt;
use std::str;

#[pyfunction]
pub fn normalize_namespace<'p>(
    py: Python<'p>,
    namespace: &Bound<'p, PyBytes>,
) -> PyResult<Bound<'p, PyBytes>> {
    if namespace.as_bytes().len() == NS_SIZE {
        Ok(namespace.clone())
    } else {
        match Namespace::new_v0(namespace.as_bytes()) {
            Ok(namespace) => PyBytes::new_with(py, namespace.0.len(), |bytes: &mut [u8]| {
                bytes.copy_from_slice(namespace.as_bytes());
                Ok(())
            }),
            Err(err) => Err(PyValueError::new_err(format!(
                "Wrong namespaces; {}",
                err.to_string()
            ))),
        }
    }
}

#[pyfunction(signature = (namespace, data, signer=None))]
pub fn normalize_blob<'p>(
    py: Python<'p>,
    namespace: &Bound<'p, PyBytes>,
    data: &Bound<'p, PyBytes>,
    signer: Option<&Bound<'p, PyBytes>>,
) -> PyResult<Bound<'p, PyDict>> {
    let namespace = match if namespace.as_bytes().len() == NS_SIZE {
        Namespace::from_raw(namespace.as_bytes())
    } else {
        Namespace::new_v0(namespace.as_bytes())
    } {
        Ok(namespace) => namespace,
        Err(err) => {
            return Err(PyValueError::new_err(format!(
                "Wrong namespaces; {}",
                err.to_string()
            )))
        }
    };

    let data = match data.extract::<Vec<u8>>() {
        Ok(data) => data,
        Err(err) => {
            return Err(PyValueError::new_err(format!(
                "Wrong blob data; {}",
                err.to_string()
            )))
        }
    };

    let blob = match signer {
        Some(signer) => {
            let signer = match signer.extract::<Vec<u8>>() {
                Ok(signer) => match AccAddress::try_from(signer) {
                    Ok(signer) => signer,
                    Err(err) => {
                        return Err(PyValueError::new_err(format!(
                            "Wrong signer address; {}",
                            err.to_string()
                        )))
                    }
                },
                Err(err) => {
                    return Err(PyValueError::new_err(format!(
                        "Wrong signer address; {}",
                        err.to_string()
                    )))
                }
            };
            match Blob::new_with_signer(namespace, data, signer, AppVersion::V3) {
                Ok(blob) => blob,
                Err(err) => {
                    return Err(PyRuntimeError::new_err(format!(
                        "Cannot create signed blob; {}",
                        err.to_string()
                    )))
                }
            }
        }
        None => match Blob::new(namespace, data, AppVersion::V3) {
            Ok(blob) => blob,
            Err(err) => {
                return Err(PyRuntimeError::new_err(format!(
                    "Cannot create blob; {}",
                    err.to_string()
                )))
            }
        },
    };

    let key_vals: Vec<(&str, PyObject)> = vec![
        ("data", PyBytes::new(py, &blob.data).into_py_any(py)?),
        (
            "namespace",
            PyBytes::new(py, &blob.namespace.0).into_py_any(py)?,
        ),
        (
            "commitment",
            PyBytes::new(py, blob.commitment.hash()).into_py_any(py)?,
        ),
        ("share_version", blob.share_version.into_py_any(py)?),
        ("index", blob.index.into_py_any(py)?),
    ];
    Ok(key_vals.into_py_dict(py)?)
}

#[pyfunction(signature = (value))]
pub fn address2bytes<'p>(
    py: Python<'p>,
    value: &Bound<'p, PyString>,
) -> PyResult<Bound<'p, PyBytes>> {
    let address: Address = match value.extract::<String>() {
        Ok(data) => match data.parse() {
            Ok(address) => address,
            Err(err) => {
                return Err(PyValueError::new_err(format!(
                    "Wrong address: {}",
                    err.to_string()
                )))
            }
        },
        Err(err) => {
            return Err(PyValueError::new_err(format!(
                "Wrong address: {}",
                err.to_string()
            )))
        }
    };
    let result = address.as_bytes();
    PyBytes::new_with(py, result.len(), |bytes: &mut [u8]| {
        bytes.copy_from_slice(result);
        Ok(())
    })
}

#[pyfunction(signature = (value))]
pub fn bytes2address<'p>(
    py: Python<'p>,
    value: &Bound<'p, PyBytes>,
) -> PyResult<Bound<'p, PyString>> {
    let address = match value.extract::<Vec<u8>>() {
        Ok(data) => match AccAddress::try_from(data.as_slice()) {
            Ok(address) => address,
            Err(err) => {
                return Err(PyValueError::new_err(format!(
                    "Wrong address: {}",
                    err.to_string()
                )))
            }
        },
        Err(err) => {
            return Err(PyValueError::new_err(format!(
                "Wrong address: {}",
                err.to_string()
            )))
        }
    };
    Ok((address.to_string().into_pyobject(py).unwrap()))
}

pub fn register_module(parent: &Bound<'_, PyModule>) -> PyResult<()> {
    let m = PyModule::new(parent.py(), "types")?;
    m.add_function(wrap_pyfunction!(address2bytes, &m)?)?;
    m.add_function(wrap_pyfunction!(bytes2address, &m)?)?;
    m.add_function(wrap_pyfunction!(normalize_namespace, &m)?)?;
    m.add_function(wrap_pyfunction!(normalize_blob, &m)?)?;
    parent.add_submodule(&m)
}
