mod types;
use pyo3::prelude::*;

#[pymodule]
fn _celestia(m: &Bound<'_, PyModule>) -> PyResult<()> {
    types::register_module(m)?;
    Ok(())
}
