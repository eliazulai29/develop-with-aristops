# ----------------------------------------------------------------------------
#
#  Welcome to Baml! To use this generated code, please run the following:
#
#  $ pip install baml
#
# ----------------------------------------------------------------------------

# This file was generated by BAML: please do not edit it. Instead, edit the
# BAML files and re-generate this code using: baml-cli generate
# baml-cli is available with the baml package.

import typing
import typing_extensions
import baml_py

from . import stream_types, types, type_builder
from .parser import LlmResponseParser, LlmStreamParser
from .runtime import DoNotUseDirectlyCallManager, BamlCallOptions
from .globals import DO_NOT_USE_DIRECTLY_UNLESS_YOU_KNOW_WHAT_YOURE_DOING_RUNTIME as __runtime__


class BamlAsyncClient:
    __options: DoNotUseDirectlyCallManager
    __stream_client: "BamlStreamClient"
    __http_request: "BamlHttpRequestClient"
    __http_stream_request: "BamlHttpStreamRequestClient"
    __llm_response_parser: LlmResponseParser
    __llm_stream_parser: LlmStreamParser

    def __init__(self, options: DoNotUseDirectlyCallManager):
        self.__options = options
        self.__stream_client = BamlStreamClient(options)
        self.__http_request = BamlHttpRequestClient(options)
        self.__http_stream_request = BamlHttpStreamRequestClient(options)
        self.__llm_response_parser = LlmResponseParser(options)
        self.__llm_stream_parser = LlmStreamParser(options)

    def with_options(self,
        tb: typing.Optional[type_builder.TypeBuilder] = None,
        client_registry: typing.Optional[baml_py.baml_py.ClientRegistry] = None,
        collector: typing.Optional[typing.Union[baml_py.baml_py.Collector, typing.List[baml_py.baml_py.Collector]]] = None,
        env: typing.Optional[typing.Dict[str, typing.Optional[str]]] = None,
    ) -> "BamlAsyncClient":
        options: BamlCallOptions = {}
        if tb is not None:
            options["tb"] = tb
        if client_registry is not None:
            options["client_registry"] = client_registry
        if collector is not None:
            options["collector"] = collector
        if env is not None:
            options["env"] = env
        return BamlAsyncClient(self.__options.merge_options(options))

    @property
    def stream(self):
      return self.__stream_client

    @property
    def request(self):
      return self.__http_request

    @property
    def stream_request(self):
      return self.__http_stream_request

    @property
    def parse(self):
      return self.__llm_response_parser

    @property
    def parse_stream(self):
      return self.__llm_stream_parser
    
    async def AnalyzeCode(self, code: str,
        baml_options: BamlCallOptions = {},
    ) -> types.CodeAnalysis:
        result = await self.__options.merge_options(baml_options).call_function_async(function_name="AnalyzeCode", args={
            "code": code,
        })
        return typing.cast(types.CodeAnalysis, result.cast_to(types, types, stream_types, False, __runtime__))
    async def AnalyzeComplexity(self, component: types.CodeComponent,
        baml_options: BamlCallOptions = {},
    ) -> str:
        result = await self.__options.merge_options(baml_options).call_function_async(function_name="AnalyzeComplexity", args={
            "component": component,
        })
        return typing.cast(str, result.cast_to(types, types, stream_types, False, __runtime__))
    


class BamlStreamClient:
    __options: DoNotUseDirectlyCallManager

    def __init__(self, options: DoNotUseDirectlyCallManager):
        self.__options = options

    def AnalyzeCode(self, code: str,
        baml_options: BamlCallOptions = {},
    ) -> baml_py.BamlStream[stream_types.CodeAnalysis, types.CodeAnalysis]:
        ctx, result = self.__options.merge_options(baml_options).create_async_stream(function_name="AnalyzeCode", args={
            "code": code,
        })
        return baml_py.BamlStream[stream_types.CodeAnalysis, types.CodeAnalysis](
          result,
          lambda x: typing.cast(stream_types.CodeAnalysis, x.cast_to(types, types, stream_types, True, __runtime__)),
          lambda x: typing.cast(types.CodeAnalysis, x.cast_to(types, types, stream_types, False, __runtime__)),
          ctx,
        )
    def AnalyzeComplexity(self, component: types.CodeComponent,
        baml_options: BamlCallOptions = {},
    ) -> baml_py.BamlStream[str, str]:
        ctx, result = self.__options.merge_options(baml_options).create_async_stream(function_name="AnalyzeComplexity", args={
            "component": component,
        })
        return baml_py.BamlStream[str, str](
          result,
          lambda x: typing.cast(str, x.cast_to(types, types, stream_types, True, __runtime__)),
          lambda x: typing.cast(str, x.cast_to(types, types, stream_types, False, __runtime__)),
          ctx,
        )
    

class BamlHttpRequestClient:
    __options: DoNotUseDirectlyCallManager

    def __init__(self, options: DoNotUseDirectlyCallManager):
        self.__options = options

    async def AnalyzeCode(self, code: str,
        baml_options: BamlCallOptions = {},
    ) -> baml_py.baml_py.HTTPRequest:
        result = await self.__options.merge_options(baml_options).create_http_request_async(function_name="AnalyzeCode", args={
            "code": code,
        }, mode="request")
        return result
    async def AnalyzeComplexity(self, component: types.CodeComponent,
        baml_options: BamlCallOptions = {},
    ) -> baml_py.baml_py.HTTPRequest:
        result = await self.__options.merge_options(baml_options).create_http_request_async(function_name="AnalyzeComplexity", args={
            "component": component,
        }, mode="request")
        return result
    

class BamlHttpStreamRequestClient:
    __options: DoNotUseDirectlyCallManager

    def __init__(self, options: DoNotUseDirectlyCallManager):
        self.__options = options

    async def AnalyzeCode(self, code: str,
        baml_options: BamlCallOptions = {},
    ) -> baml_py.baml_py.HTTPRequest:
        result = await self.__options.merge_options(baml_options).create_http_request_async(function_name="AnalyzeCode", args={
            "code": code,
        }, mode="stream")
        return result
    async def AnalyzeComplexity(self, component: types.CodeComponent,
        baml_options: BamlCallOptions = {},
    ) -> baml_py.baml_py.HTTPRequest:
        result = await self.__options.merge_options(baml_options).create_http_request_async(function_name="AnalyzeComplexity", args={
            "component": component,
        }, mode="stream")
        return result
    

b = BamlAsyncClient(DoNotUseDirectlyCallManager({}))