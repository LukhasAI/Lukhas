from interfaces.api.v1.rest.models import ProcessingMode, ProcessRequest


def test_process_request_validation():
    req = ProcessRequest(input_text="hello", mode=ProcessingMode.SYMBOLIC)
    assert req.input_text == "hello"
    assert req.mode == ProcessingMode.SYMBOLIC
