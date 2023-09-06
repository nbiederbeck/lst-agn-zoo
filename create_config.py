import yaml
import json
from pprint import pprint
from pathlib import Path
import logging


log = logging.getLogger(__name__)


gammapy_skeleton = """
general:
  log:
    level: info

observations:
  datastore: build/<<source_name>>/dl3
  obs_time:
    start: "<<data_start>>"
    stop: "<<data_end>>"
  required_irf:
    - aeff
    - edisp

datasets:
  type: 1d
  stack: true
  geom:
    wcs:
      skydir: { frame: icrs, lon: <<source_ra>> deg, lat: <<source_dec>> deg }
      binsize: 0.02 deg
      width: { width: 2.0 deg, height: 2.0 deg }
      binsize_irf: 0.2 deg
    selection: { offset_max: 2.5 deg }
    axes:
      energy:
        min: 20 GeV
        max: 10 TeV
        nbins: 40
      energy_true:
        min: 20 GeV
        max: 10 TeV
        nbins: 20
  background:
    method: "reflected"
    parameters: { min_distance_input: 1 deg }
  on_region:
    { frame: icrs, lon: <<source_ra>> deg, lat: <<source_dec>> deg, radius: 0.2 deg }
  containment_correction: false

fit:
  fit_range: { min: 20 GeV, max: 10 TeV }

flux_points:
  energy: { min: 20 GeV, max: 10 TeV, nbins: 20 }
  source: <<source_name>>

light_curve:
  energy_edges: { min: 100 GeV, max: 10 TeV, nbins: 1 }
  source: <<source_name>>
"""


model_skeleton = """
components:
- name: <<source_name>>
  type: SkyModel
  spectral:
    type: PowerLawSpectralModel
    parameters:
    - name: amplitude
      value: 6.0e-11
      unit: cm-2 s-1 TeV-1
      min: 0
    - name: index
      value: 2.2
      unit: ''
    - name: reference
      value: 100
      unit: GeV
      frozen: true
"""

selection_skeleton = """
{
  "source": "<<source_name>>",
  "source_ra_deg": <<source_ra>>,
  "source_dec_deg": <<source_dec>>,
  "pedestal": { "ul": 1.9, "ll": null, "sigma": null },
  "cosmics": { "ul": 7800, "ll": 2600, "sigma": null },
  "cosmics_10": { "ul": null, "ll": null, "sigma": null },
  "cosmics_30": { "ul": null, "ll": null, "sigma": null },
  "time_start": "<<data_start>>",
  "time_stop": "<<data_end>>",
  "always_include": [],
  "never_include": []
}
"""


irf_skeleton = """
{
  "DL3Cuts": {
    "max_gh_cut": 1.0,
    "min_gh_cut": 0.4,
    "gh_efficiency": 0.8,
    "max_theta_cut": 0.35,
    "fill_theta_cut": 0.35,
    "min_theta_cut": 0.05,
    "theta_containment": 0.68
  },
  "IRFFITSWriter": {
    "energy_dependent_theta": true,
    "energy_dependent_gh": true,
    "point_like": true,
    "overwrite": true
  },
  "DataReductionFITSWriter": {
    "source_ra": "<<source_ra>> deg",
    "source_dec": "<<source_dec>> deg"
  }
}
"""

snakemake_skeleton = """
{
  "production": "<<mc_production>>",
  "declination": "<<mc_dec_line>>",
  "lstchain_enviroment": "lstchain-v0.9.13",
  "n_off_regions": 1
}
"""

skeletons = [snakemake_skeleton, selection_skeleton, irf_skeleton, gammapy_skeleton, model_skeleton]

def main():
    log.level = logging.INFO
    source_name = input("Input source name: ")
    output_dir = Path(source_name)
    if output_dir.exists():
        raise IOError("Directory {output_dir} already exists!")

    output_dir.mkdir()
    gammapy_dir = output_dir / "analysis-baseline-powerlaw"
    gammapy_dir.mkdir()


    # These will probably always be the same?
    mc_production = "20230127_v0.9.12_base_prod_az_tel"
    data_start = "2020-05-01"
    data_end = "2022-07-01"

    source_ra = input("Input source right ascension in units of deg (position.ra in icrs): ")
    source_dec = input("Input source declination in units of deg (position.dec in icrs): ")
    mc_dec_line = input(f"Which mc dec line (of prod {mc_production}) should be used? ")

    def replace(s):
        s = s.replace("<<mc_production>>", mc_production)
        s = s.replace("<<mc_dec_line>>", mc_dec_line)
        s = s.replace("<<source_name>>", source_name)
        s = s.replace("<<source_ra>>", source_ra)
        s = s.replace("<<source_dec>>", source_dec)
        s = s.replace("<<data_start>>", data_start)
        s = s.replace("<<data_end>>", data_end)
        return s


    with open(output_dir / "lst_agn.json", 'w', encoding='utf-8') as f:
        agn_config = json.loads(replace(snakemake_skeleton))
        json.dump(agn_config, f, ensure_ascii=False, indent=4, separators=(',', ': '))

    with open(output_dir / "data_selection.json", 'w', encoding='utf-8') as f:
        pprint(replace(selection_skeleton))
        selection_config = json.loads(replace(selection_skeleton))
        json.dump(selection_config, f, ensure_ascii=False, indent=4, separators=(',', ': '))

    with open(output_dir / "irf_tool_config.json", 'w', encoding='utf-8') as f:
        pprint(replace(irf_skeleton))
        irf_config = json.loads(replace(irf_skeleton))
        json.dump(irf_config, f, ensure_ascii=False, indent=4, separators=(',', ': '))

    with open(gammapy_dir / "analysis.yaml", 'w', encoding='utf-8') as f:
        analysis_config = yaml.safe_load(replace(gammapy_skeleton))
        yaml.dump(analysis_config, f)

    with open(gammapy_dir / "models.yaml", 'w', encoding='utf-8') as f:
        model_config = yaml.safe_load(replace(model_skeleton))
        yaml.dump(model_config, f)

    log.info(f"Wrote basic workflow configs to {output_dir}")
    log.info("Make sure to check everything especially the data selection!")
    log.info("There are a lot of default values in there that differ per source")
    log.info("You can add multiple 'analysis-*' subdirs for different gammapy settings")


if __name__ == "__main__":
    main()



