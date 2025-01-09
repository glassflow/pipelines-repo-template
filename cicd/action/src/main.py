from yaml import safe_load
from pathlib import Path
from models import Pipeline
from glassflow import GlassFlowClient, Pipeline as GlassFlowPipeline
import itertools


def load_pipeline_from_yaml(yaml_file):
    # Load YAML
    with open(yaml_file) as f:
        yaml_data = safe_load(f)

    return Pipeline(**yaml_data)


def yaml_pipeline_to_sdk_pipeline(yaml_path: Path, personal_access_token: str) -> GlassFlowPipeline:
    """
    Converts a YAML pipeline into GlassFlow sdk pipeline
    Only one function is allowed
    """
    pipeline_path = yaml_path.parent
    pipeline = load_pipeline_from_yaml(yaml_path)

    # We have one source, transformer and sink blocks
    source = [b for b in pipeline.blocks if b.type == "source"][0]
    transform_block = [b for b in pipeline.blocks if b.type == "transformer"][0]
    sink = [b for b in pipeline.blocks if b.type == "sink"][0]

    if transform_block.requirements is not None:
        if transform_block.requirements.value is not None:
            requirements = transform_block.requirements.value
        else:
            with open(pipeline_path / transform_block.requirements.path) as f:
                requirements = f.read()
    else:
        requirements = None

    if transform_block.transformation.path is not None:
        transform = str(pipeline_path / transform_block.transformation.path)
    else:
        transform = str(pipeline_path / "handler.py")
        with open(transform, "w") as f:
            f.write(transform_block.transformation.value)

    pipeline_id = str(pipeline.pipeline_id) if pipeline.pipeline_id is not None else None

    # TODO: Handle source and sink config_secret_ref
    # TODO: Handle env_var value_secret_ref
    return GlassFlowPipeline(
        personal_access_token=personal_access_token,
        id=pipeline_id,
        name=pipeline.name,
        space_id=pipeline.space_id.__str__(),
        env_vars=[e.model_dump(exclude_none=True) for e in transform_block.env_vars],
        transformation_file=transform,
        requirements=requirements,
        sink_kind=sink.kind,
        sink_config=sink.config,
        source_kind=source.kind,
        source_config=source.config
    )


def get_pipelines_changed(pipelines_dir: str, files_changed: list[str]) -> set[Path]:
    pipelines_dir = Path(pipelines_dir)

    pipeline_2_files = map_yaml_to_files(pipelines_dir)

    pipelines_changed = set()
    for file in files_changed:
        file = Path(file)

        if file.suffix in [".yaml", ".yml"]:
            if pipelines_dir in file.parents:
                pipelines_changed.add(file)
            else:
                # Ignore YAML files outside pipelines dir
                continue
        elif file.suffix == ".py" or file.name == "requirements.txt":
            for k, v in pipeline_2_files.items():
                if file in pipeline_2_files[k]:
                    pipelines_changed.add(k)
        else:
            continue

    return pipelines_changed


def map_yaml_to_files(pipelines_dir: Path) -> dict[Path, list[Path]]:
    yml_files = itertools.chain(pipelines_dir.rglob("*.yaml"), pipelines_dir.rglob("*.yml"))
    mapping = {}
    for file in yml_files:
        mapping[file] = []
        pipeline = load_pipeline_from_yaml(file)
        transformer = [b for b in pipeline.blocks if b.type == "transformer"][0]

        if transformer.requirements.path is not None:
            path = file.parent / transformer.requirements.path
            mapping[file].append(path)

        if transformer.transformation.path is not None:
            path = file.parent / transformer.transformation.path
            mapping[file].append(path)
    return mapping


if __name__ == '__main__':
    # TODO: Figure out how github gives root path for repo
    personal_access_token = "wBtaqZKS9eh37FsWcE8YsY9SpxtvmGKra2kRv4vjyVSSgyaVfSnj7h9GP8X33mZn4hfBEDDTvcMWMX8gK329Wx92KyeP8TjGsMhpS5vcc8XT3KnAPmg7SRHnTym8tzp2"
    client = GlassFlowClient(personal_access_token=personal_access_token)
    pipelines_to_update = get_pipelines_changed(
        pipelines_dir="../../../pipelines",
        files_changed=[
            "../../../pipelines/simple_pipeline/pipeline.yaml",
            "../../../pipelines/simple_pipeline/handler.py",
            "../../../pipelines/test/a/handler.py"
        ]
    )
    for pipeline in pipelines_to_update:
        sdk_pipeline = yaml_pipeline_to_sdk_pipeline(pipeline, personal_access_token)

        if sdk_pipeline.id is None:
            # Create pipeline
            pipeline = sdk_pipeline.create()
            # TODO: Fill pipeline_id in YAML and commit changes
        else:
            # Update pipeline
            pipeline = client.get_pipeline(sdk_pipeline.id)
            pipeline.update(
                name=sdk_pipeline.name,
                transformation_file=sdk_pipeline.transformation_file,
                requirements=sdk_pipeline.requirements,
                sink_kind=sdk_pipeline.sink_kind,
                sink_config=sdk_pipeline.sink_config,
                source_kind=sdk_pipeline.source_kind,
                source_config=sdk_pipeline.source_config,
                env_vars=sdk_pipeline.env_vars
            )
