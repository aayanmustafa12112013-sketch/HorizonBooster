// Change only the periodic sweep interval; the area-change trigger is untouched.
fn modify(value: u8) -> u8 {
    crate::streaming::horizon_optimizer::sweep_interval(value)
}
