// Horizon Booster: reduce the frequency of full loaded-chunk/proto range sweeps.
// The sweep still runs immediately whenever the player's center or view radius changes.

pub fn sweep_interval(original: u8) -> u8 {
    if original == 8 { 16 } else { original }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn doubles_periodic_sweep_interval_without_changing_other_values() {
        assert_eq!(sweep_interval(8), 16);
        assert_eq!(sweep_interval(4), 4);
        assert_eq!(sweep_interval(16), 16);
    }
}
