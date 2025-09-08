import pandas as pd
import pydantic
import pytest

from retrack.nodes import dynamic_nodes_registry


@pytest.fixture
def glm_metadata():
    return {
        "id": "53e6fe5413a32be7",
        "name": "GLM",
        "data": {
            "value": '{"a":2,"b":0.5,"intercept":1}',
            "link": "identity",
            "headers_map": {"a": 0, "b": 1},
        },
        "outputs": {
            "output_value": {
                "connections": [{"node": "9c7b5cca67565955", "input": "input_value"}]
            }
        },
        "inputs": {
            "input_value_0": {
                "connections": [{"node": "e3ff3420e884087e", "output": "output_value"}]
            },
            "input_value_1": {
                "connections": [{"node": "a59c1209bf437061", "output": "output_value"}]
            },
        },
    }


def test_get_glm_factory():
    glm_factory = dynamic_nodes_registry().get("GLM")

    assert callable(glm_factory)


def test_create_glm_from_factory(glm_metadata):
    glm_factory = dynamic_nodes_registry().get("GLM")
    GLM = glm_factory(**glm_metadata)

    assert issubclass(GLM, pydantic.BaseModel)

    model = GLM(**glm_metadata)

    assert isinstance(model, GLM)
    assert hasattr(model, "run")


@pytest.mark.asyncio
async def test_glm_run(glm_metadata):
    glm_factory = dynamic_nodes_registry().get("GLM")
    GLM = glm_factory(**glm_metadata)

    model = GLM(**glm_metadata)

    payload = {
        "input_value_0": pd.Series([1, 2, -1]),
        "input_value_1": pd.Series(["4", "3", "-1"]),
    }

    expected = pd.Series([5, 6.5, -1.5])

    response = await model.run(**payload)
    assert response["output_value"].equals(expected)


@pytest.mark.asyncio
async def test_glm_run_without_intercept(glm_metadata):
    glm_metadata["data"]["value"] = '{"a":2,"b":0.5}'
    glm_metadata["data"]["intercept"] = None

    glm_factory = dynamic_nodes_registry().get("GLM")
    GLM = glm_factory(**glm_metadata)

    model = GLM(**glm_metadata)

    payload = {
        "input_value_0": pd.Series([1, 2, -1]),
        "input_value_1": pd.Series(["4", "3", "-1"]),
    }

    expected = pd.Series([4, 5.5, -2.5])

    response = await model.run(**payload)
    assert response["output_value"].equals(expected)


@pytest.mark.asyncio
async def test_glm_run_with_missing_input(glm_metadata):
    with pytest.raises(ValueError, match="Missing input input_value_1 in GLM node"):
        glm_factory = dynamic_nodes_registry().get("GLM")
        GLM = glm_factory(**glm_metadata)

        model = GLM(**glm_metadata)

        payload = {
            "input_value_0": pd.Series([1, 2, -1]),
        }

        _ = await model.run(**payload)


@pytest.mark.asyncio
async def test_glm_run_with_missing_weight(glm_metadata):
    with pytest.raises(ValueError, match="Missing weight for feature a in GLM node"):
        glm_metadata["data"]["value"] = '{"intercept":1}'

        glm_factory = dynamic_nodes_registry().get("GLM")
        GLM = glm_factory(**glm_metadata)

        model = GLM(**glm_metadata)

        payload = {
            "input_value_0": pd.Series([1, 2, -1]),
            "input_value_1": pd.Series(["4", "3", "-1"]),
        }

        _ = await model.run(**payload)
