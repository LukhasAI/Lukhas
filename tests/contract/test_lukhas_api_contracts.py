"""Contract tests for the LUKHAS API."""
import aiohttp
import pytest
from pact import Consumer, Provider
from pact.matchers import Like, Term

# Define the consumer and provider
pact = Consumer('LukhasWebConsumer').has_pact_with(
    Provider('LukhasAPI'),
    pact_dir='./pacts',
    host_name='localhost',
    port=8000
)


@pytest.mark.asyncio
async def test_create_response_contract():
    """Test the /v1/responses endpoint contract."""
    # Define the expected request
    expected_request = {
        'method': 'POST',
        'path': '/v1/responses',
        'headers': {'Content-Type': 'application/json'},
        'body': {
            'model': 'lukhas-mini',
            'input': 'hello',
        },
    }

    # Define the expected response, using matchers for dynamic values
    expected_response = {
        'status': 200,
        'headers': {'Content-Type': 'application/json; charset=utf-8'},
        'body': {
            'id': Like('resp_...'),
            'object': 'chat.completion',
            'created': Like(1677649420),
            'model': 'lukhas-mini',
            'choices': [
                {
                    'index': 0,
                    'message': {
                        'role': 'assistant',
                        'content': Term(
                            generate='[stub] hello',
                            matcher=r'\[stub\] .+'
                        ),
                    },
                    'finish_reason': 'stop',
                }
            ],
            'usage': {
                'prompt_tokens': Like(1),
                'completion_tokens': Like(2),
                'total_tokens': Like(3),
            },
        },
    }

    # Add the interaction to the pact
    (pact
     .given('a request to the responses endpoint')
     .upon_receiving('a request for a simple response')
     .with_request(**expected_request)
     .will_respond_with(expected_response))

    # Verify the pact
    with pact:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f'{pact.uri}/v1/responses',
                json={'model': 'lukhas-mini', 'input': 'hello'},
                headers={'Content-Type': 'application/json'}
            ) as response:
                assert response.status == 200
