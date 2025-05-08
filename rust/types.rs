use celestia_types::nmt::{Namespace, NS_SIZE};
use celestia_types::{AppVersion, Blob};
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{IntoPyDict, PyBytes, PyDict, PyInt};
use pyo3::IntoPyObjectExt;

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

#[pyfunction]
pub fn normalize_blob<'p>(
    py: Python<'p>,
    namespace: &Bound<'p, PyBytes>,
    data: &Bound<'p, PyBytes>,
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
    let blob = match Blob::new(namespace, data, AppVersion::V3) {
        Ok(blob) => blob,
        Err(err) => {
            return Err(PyRuntimeError::new_err(format!(
                "Cannot create blob; {}",
                err.to_string()
            )))
        }
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

pub fn register_module(parent: &Bound<'_, PyModule>) -> PyResult<()> {
    let m = PyModule::new(parent.py(), "types")?;
    m.add_function(wrap_pyfunction!(normalize_namespace, &m)?)?;
    m.add_function(wrap_pyfunction!(normalize_blob, &m)?)?;
    parent.add_submodule(&m)
}
