#!/usr/bin/env python3
"""Compile the real bundle on a tiny streaming fixture; no Horizon/assets needed."""
import json
from pathlib import Path
import subprocess
import tempfile
import tomllib
import horizon


def run(command, **kwargs):
    result = subprocess.run(command, capture_output=True, text=True, **kwargs)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result


def snapshot(root):
    return {str(p.relative_to(root)): (horizon.digest(p.read_bytes()), p.stat().st_mtime_ns)
            for p in root.rglob('*') if p.is_file()}


def audit(original, stage, plan):
    run(['cargo', 'run', '--quiet', '--locked', '--offline', '-p', 'native-mod-source-audit',
         '--', str(original), str(stage), str(plan)], cwd=horizon.ROOT)


def main():
    root = horizon.ROOT
    (root/'target').mkdir(exist_ok=True)
    run(['cargo', 'build', '--locked', '--offline', '-p', 'horizon-mixins-cli'], cwd=horizon.MIXINS)
    cli = horizon.MIXINS/'target/debug/horizon-mixins'
    manifests = list((root/'mixins').glob('*/horizon-mixin.toml'))
    assert len(manifests) == 1, 'expected exactly one native bundle'
    manifest = tomllib.loads(manifests[0].read_text())

    with tempfile.TemporaryDirectory(prefix='optimizer-test-', dir=root/'target') as scratch:
        scratch = Path(scratch)
        original, stage = scratch/'original', scratch/'stage'
        source_dir = original/'crates/horizon-client-render/src'
        source_dir.mkdir(parents=True)
        (original/'Cargo.toml').write_text(
            '[workspace]\\nmembers=["crates/horizon-client-render"]\\nresolver="2"\\n')
        (original/'crates/horizon-client-render/Cargo.toml').write_text(
            '[package]\\nname="horizon-client-render"\\nversion="0.1.0"\\nedition="2024"\\n')
        (source_dir/'lib.rs').write_text('pub mod streaming;\\n')
        (source_dir/'streaming.rs').write_text("""
pub struct Streaming { pub center: (i32, i32), pub scan_center: (i32, i32), pub scan_age: u8 }
impl Streaming {
    pub fn update(&mut self) -> bool {
        let area_changed = self.center != self.scan_center;
        let sweep = area_changed || self.scan_age >= 8;
        self.scan_center = self.center;
        self.scan_age = if sweep { 0 } else { self.scan_age + 1 };
        sweep
    }
}
#[test] fn periodic_sweep_and_area_change_are_preserved() {
    let mut s = Streaming { center: (0,0), scan_center: (0,0), scan_age: 16 };
    assert!(s.update());
    s.scan_age = 15;
    assert!(!s.update());
    s.center = (1,0);
    assert!(s.update());
}
""")
        (original/'rust-toolchain.toml').write_bytes((root/'rust-toolchain.toml').read_bytes())
        (original/'.horizon-revision').write_text(horizon.PIN+'\\n')
        run(['cargo', 'generate-lockfile', '--offline'], cwd=original)
        before = snapshot(original)
        base = ['--workspace', str(original), '--mods', str(root/'mixins')]
        report = json.loads(run([str(cli), 'check', *base, '--out', str(stage),
                                 '--trust-native-mods']).stdout)
        assert report['injections'] == 1 and report['modules'] == 1
        assert '2 passed' in report['cargo_stdout']
        first = snapshot(stage)
        second = json.loads(run([str(cli), 'check', *base, '--out', str(stage),
                                 '--trust-native-mods']).stdout)
        assert not second['stage_changed'] and snapshot(stage) == first
        assert snapshot(original) == before

        plan_path = scratch/'plan.json'
        run([str(cli), 'plan', *base, '--out', str(plan_path)])
        plan = json.loads(plan_path.read_text())
        assert plan['schema'] == horizon.COMPAT['mixin_schema']
        assert plan['injections'][0]['mod_id'] == manifest['mod']['id']
        audit(original, stage, plan_path)

        (original/'.horizon-revision').write_text('incompatible\\n')
        bad = subprocess.run([str(cli), 'apply', *base, '--out', str(stage)],
                             capture_output=True, text=True)
        assert bad.returncode and json.loads(bad.stderr)['code'] == 'E_REVISION'
        assert snapshot(stage) == first

        (original/'.horizon-revision').write_text(horizon.PIN+'\\n')
        source = source_dir/'streaming.rs'
        source.write_text(source.read_text().replace('pub fn update', 'pub fn renamed_update'))
        bad = subprocess.run([str(cli, 'apply', *base, '--out', str(stage)],
                             capture_output=True, text=True)
        assert bad.returncode and json.loads(bad.stderr)['code'] == 'E_TARGET_NOT_FOUND'
        assert snapshot(stage) == first

    print(json.dumps({'status': 'ok', 'compiled_runtime_and_streaming_fixture': True,
                      'only_planned_asts_changed': True, 'deterministic_bytes_and_mtimes': True,
                      'incompatible_revision_and_target_rejected': True}, indent=2))


if __name__ == '__main__':
    main()
