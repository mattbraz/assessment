import os
import time
from behave import *
from api import API, CommonTests


def get_api_params():
    params = {
        'base_url': os.environ.get('API_BASE_URL'),
        'key': os.environ.get('API_KEY'),
        'secret': os.environ.get('API_SEC'),
        'otp': os.environ.get('API_OTP'),
    }
    return params


@given('I have an API connection')
def step_impl(context):
    context.api = API(**get_api_params())

@given('I have an API connection with missing otp')
def step_impl(context):
    params = get_api_params()
    params['otp'] = None
    context.api = API(**params)

@then('the request should finish in under {secs} seconds')
def step_impl(context, secs):
    assert context.response.elapsed.total_seconds() < float(secs)


@given('I request the server time')
def step_impl(context):
    context.response = context.api.get_server_time()

@then('I should receive a valid server time response')
def step_impl(context):
    CommonTests.http_checks(context.response)
    CommonTests.basic_api_checks(context.response)
    CommonTests.check_fields_server_time(context.response)
    data = context.response.json()
    assert time.time() - data['result']['unixtime'] <= 50


@given('I request the asset pair {pair}')
def step_impl(context, pair):
    context.pair = pair
    context.response = context.api.get_asset_pair(pair)

@then('I should receive a valid asset pair response')
def step_impl(context):
    CommonTests.http_checks(context.response)
    CommonTests.basic_api_checks(context.response)
    CommonTests.check_fields_asset_pairs(context.response)

@then('the asset pair response should contain the alias {alias}')
def step_impl(context, alias):
    data = context.response.json()
    print(data['result'][context.pair])
    assert data['result'][context.pair]['altname'] == alias


@given('I request the open orders')
def step_impl(context):
    context.response = context.api.get_open_orders()

@then('I should receive a valid open orders response')
def step_impl(context):
    CommonTests.http_checks(context.response)
    CommonTests.basic_api_checks(context.response)
    CommonTests.check_fields_open_orders(context.response)

@then('I should receive an error "{error}" response')
def step_impl(context, error):
    CommonTests.http_checks(context.response)
    data = context.response.json()
    assert 'error' in data
    assert data['error'] == [error]

