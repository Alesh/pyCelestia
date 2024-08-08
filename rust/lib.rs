use celestia_types::Commitment;
use celestia_types::nmt::Namespace;
use pyo3::prelude::*;
use pyo3::types::PyBytes;


/// Generate the share commitment from the given blob data.
#[pyfunction]
#[pyo3(signature = (ns, data, share_version = 0))]
pub fn make_commitment(py: Python, ns: &[u8], data: &[u8], share_version: u64) -> PyObject {
    let result = Namespace::from_raw(ns);
    let namespace = match result {
        Ok(namespace) => namespace,
        Err(_) => Namespace::new_v0(ns).expect("Invalid namespace"),
    };
    let commitment = Commitment::from_blob(namespace, share_version as u8, &data[..]).expect("Cannot make commitment");
    PyBytes::new_bound(py, &commitment.0).into()
}

#[pymodule]
#[pyo3(name = "_types")]
fn _celestia(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction_bound!(make_commitment, m)?)?;
    Ok(())
}