<p align="center">
  <a href="https://bitbucket.dev.aws.singtel.com/projects/AIS/repos/ai-datasteward"><img src="https://github.com/Praveengovianalytics/AIaaS_falcon/raw/master/img/AIAAS_FALCON.jpg" alt="AIaaS_LLM"></a>
</p>
<p align="center">
    <em>Brainwave, high performance, easy to use, fast to infer, ready for production</em>
</p>
<p align="center">

<a href="https://pypi.org/project/fastapi" target="_blank">
    <img src="https://img.shields.io/pypi/v/aiaas-falcon?color=%2334D058&label=pypi%20package" alt="Package version">
</a>
<a href="https://pypi.org/project/fastapi" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/aiaas-falcon.svg?color=%2334D058" alt="Supported Python versions">
</a>
</p>

---

**Documentation**: Confluence

**Source Code**: <a href="https://bitbucket.dev.aws.singtel.com/projects/AIS/repos/ai-datasteward" target="_blank">https://bitbucket.dev.aws.singtel.com/projects/AIS/repos/ai-datasteward</a>

---

This repository constitutes the foundational backend infrastructure for the BrainWave Application. The application is primarily built upon the FastAPI framework to serve as the backbone for its API functionalities. It mandates the use of Python version 3.10.0 or higher to ensure compatibility and optimal performance.

Notably, the application leverages the Langchain library to facilitate the seamless loading of the underlying LLM model, showcasing a commitment to robust and cutting-edge technology integration. This repository serves as the cornerstone for the BrainWave Application's server-side operations, enabling efficient data processing and interaction with the LLM.

The key features are:

* **Fast**: Very high performance, on par with 7b, 13b and 34b gguf models
* **Easy**: Designed to be easy to use and learn. Less time reading data and documentations.
* **Short**: Minimize time spent on finding and analysing data.

## Sponsors

<!-- sponsors -->
No Sponsors for Now
<!-- /sponsors -->

## Requirements

Python 3.9+
LLamaCpp
Fastapi
Transformers 
Sentence-Transformers
Uvicorn

## Installation

<div class="termy">

```console
$ git clone https://bitbucket.dev.aws.singtel.com/scm/ais/ai-datasteward.git -b master

---> 100%
```

</div>

You will also need an ASGI server, for production:  <a href="https://www.uvicorn.org" class="external-link" target="_blank">Uvicorn</a>.

<div class="termy">

```console
$ pip install "uvicorn[standard]"

---> 100%
```

</div>

## Example

### Run it

Run the server with:

<div class="termy">

```console
$ python main.py

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28720]
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

</div>

<details markdown="1">
<summary>About the command <code> python main.py --port 8000  </code>...</summary>

The command `python main.py` refers to:

* `main`: the file `main.py` (the Python "module").
* `port`: the port number


</details>

### Check it

Open your browser at <a href="http://127.0.0.1:8000/v1/chat/ping" class="external-link" target="_blank">http://127.0.0.1:8000/v1/chat/ping</a>.

You will see the JSON response as:

```JSON
{"status":"healthy"}
```

You already started the backend API server successfully.


### Making Postman Request

#### Login

In order to retrieve a JWT token for API access, you need to first request the /v1/auth/login API.
![image](https://github.com/Praveengovianalytics/AIaaS_LLM/assets/59607914/9d4782a5-0de6-4d5f-8f56-7a79e3032e99)

Copy the token to the authentication header and you are good to go.
![image](https://github.com/Praveengovianalytics/AIaaS_LLM/assets/59607914/53645965-6474-4afd-86b5-b80e272248de)

#### Create New API Key
In order to use the Falcon Library, a API Key need to be created. The request URL is /v1/auth/register_api_key.
The Body needed are as of the following:

{

    "username":"SINGTEL USERNAME (START WITH P)",
    "project":"PROJECT_CODE",
    "department":"DEPARTMENT",
    "email":"SINGTEL EMAIL",
    "day":20
}

*Please Note that Bearer Token is needed for this API*

![image](https://github.com/Praveengovianalytics/AIaaS_LLM/assets/59607914/3348c403-5c3f-4625-ad3f-ec542d4de78f)


#### Create Embedding
Now, we will upload the file to create the embedding for chat.
First, go to body, switch the content mode to form-data and fill in the fields. The type can either be a 'general' or 'data' according to your needs.
- General Mode will be for general enquires.
- Data Mode will enable pandas based conversation where number and count is important.
*Please Note that Bearer Token is needed for this API*

![image](https://github.com/Praveengovianalytics/AIaaS_LLM/assets/59607914/21c8ed82-9b30-4a18-9ad4-70ccff5685f2)

#### Set Model

Now, we should initialize the model for usage. The list of models available can be retrieve by GET /v1/chat/get_model. The data pandas mode models does not support custom params at the moment.
![image](https://github.com/Praveengovianalytics/AIaaS_LLM/assets/59607914/c8483468-9b49-4b82-9009-039cd74185d6)

#### Predict

Finally, we can make predictions. 
- "query": What we want to ask
- "config": The configuration must be set same as what we set for "Set Model" API. 
- "conversation_config": Chat config can be adjusted according to custom need and document size for effective query
- "use_default": Deprecated
- "type": "general" or "data"
*Please Note that Bearer Token is needed for this API*

![image](https://github.com/Praveengovianalytics/AIaaS_LLM/assets/59607914/3b5016c9-eba1-442b-93ce-fea7dba6e5ee)


### Interactive API docs

Now go to <a href="http://127.0.0.1:8000/docs" class="external-link" target="_blank">http://127.0.0.1:8000/docs</a>.

You will see the automatic interactive API documentation (provided by <a href="https://github.com/swagger-api/swagger-ui" class="external-link" target="_blank">Swagger UI</a>):

![Swagger UI](https://fastapi.tiangolo.com/img/index/index-01-swagger-ui-simple.png)


### Alternative API docs

And now, go to <a href="http://127.0.0.1:8000/redoc" class="external-link" target="_blank">http://127.0.0.1:8000/redoc</a>.

You will see the alternative automatic documentation (provided by <a href="https://github.com/Rebilly/ReDoc" class="external-link" target="_blank">ReDoc</a>):

![ReDoc](https://fastapi.tiangolo.com/img/index/index-02-redoc-simple.png)






## Performance

To Be Filled

