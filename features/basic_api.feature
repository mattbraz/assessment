Feature: testing parts of the REST API

  Scenario: test server time
      Given I have an API connection
        And I request the server time
       Then I should receive a valid server time response
        And the request should finish in under 0.75 seconds

  Scenario: test get asset pairs
      Given I have an API connection
        And I request the asset pair XXBTZUSD
       Then I should receive a valid asset pair response
        And the asset pair response should contain the alias XBTUSD
        And the request should finish in under 1.5 seconds

  Scenario: test get open orders
      Given I have an API connection
        And I request the open orders
       Then I should receive a valid open orders response
        And the request should finish in under 1.5 seconds

  Scenario: test get open orders with missing otp
      Given I have an API connection with missing otp
        And I request the open orders
       Then I should receive an error "EAPI:Invalid key" response
        And the request should finish in under 1.5 seconds

