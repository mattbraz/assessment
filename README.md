# assessment

How to run
----------

Modify `env.list` with the API details and your credentials.  At the minimum you must populate `API_BASE_URL` which is the host and domain of the endpoints (e.g api.foo.com).  You can also add the key, secret and the 2FA one time password you have set up.

Run the following in the root directory of the project to build the docker image:

    docker build --tag assessment .

To run and report the Gherkin tests in the terminal run:

    docker run --env-file env.list assessment
    
Description
-----------

The project uses the `behave` BDD test framework for python.
I went for a blend of testing the completeness and validity of headers and json response fields, and some basic testing of error conditions.
I did not include a lot in the way of 'semantic' tests like 'is the fee structure of this asset correct?' etc, as these could have been fragile without a detailed spec.  I added a performance test that checks response time is acceptable (set to a wide range).
I was not able to test with actual open orders detail (I couldn't place any orders), so hopefully if you test with an account that does then it will work :).  First time with BDD and docker for me, so a fun learning experience.
