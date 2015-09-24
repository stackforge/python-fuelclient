#    Copyright 2014 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from functools import wraps
import json
from keystoneclient.exceptions import Unauthorized
import requests
import sys
import traceback


def exit_with_error(message):
    """
    Writes message to stderr and exits with exit code 1.
    """
    sys.stderr.write(message + "\n")
    exit(1)


def exit_with_traceback():
    """
    Writes traceback to stderr and exits with exit code 1.
    """
    sys.stderr.write(traceback.format_exc())
    exit(1)


def exit_with_error_or_traceback(exception, message=None):
    """
    If debug mode is on then exit with traceback, otherwise exit with
    given `message`. If `message` is not provided then it takes from the
    given `exception`.
    """
    from fuelclient.client import APIClient
    if not APIClient.debug:
        if not message:
            message = str(exception)
        exit_with_error(message)
    else:
        exit_with_traceback()


class FuelClientException(Exception):
    """Base Exception for Fuel-Client

    All child classes must be instantiated before raising.
    """
    def __init__(self, *args, **kwargs):
        super(FuelClientException, self).__init__(*args, **kwargs)
        self.message = args[0]


class BadDataException(FuelClientException):
    """Should be raised when user provides corrupted data."""


class WrongEnvironmentError(FuelClientException):
    """Raised when particular action is not supported on environment."""


class ServerDataException(FuelClientException):
    """ServerDataException - must be raised when
    data returned from server cannot be processed by Fuel-Client methods.
    """


class DeployProgressError(FuelClientException):
    """DeployProgressError - must be raised when
    deployment process interrupted on server.
    """


class ArgumentException(FuelClientException):
    """ArgumentException - must be raised when
    incorrect arguments inputted through argparse or some function.
    """


class ActionException(FuelClientException):
    """ActionException - must be raised when
    though arguments inputted to action are correct but they contradict
    to logic in action.
    """


class ParserException(FuelClientException):
    """ParserException - must be raised when
    some problem occurred in process of argument parsing,
    in argparse extension or in Fuel-Client Parser submodule.
    """


class ProfilingError(FuelClientException):
    """Indicates errors and other issues related to performance profiling."""


class SettingsException(FuelClientException):
    """Indicates errors or unexpected behaviour in processing settings."""


class ExecutedErrorNonZeroExitCode(FuelClientException):
    """Subshell command returned non-zero exit code."""


class LabelEmptyKeyError(BadDataException):
    """Should be raised when user provides labels with empty key."""


class InvalidDirectoryException(FuelClientException):
    """Indicates that a directory is not valid."""


class InvalidFileException(FuelClientException):
    """Indicates that a file is not valid."""


def exceptions_decorator(func):
    """Handles HTTP errors and expected exceptions that may occur
    in methods of APIClient class
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        # when server returns to us bad request check that
        # and print meaningful reason
        except requests.HTTPError as exc:
            exit_with_error_or_traceback(
                exc, "{0} ({1})".format(exc, get_error_body(exc)))
        except requests.ConnectionError:
            exit_with_error("""
            Can't connect to Nailgun server!
            Please modify "SERVER_ADDRESS" and "LISTEN_PORT"
            in the file /etc/fuel/client/config.yaml""")
        except Unauthorized:
            exit_with_error("""
            Unauthorized: need authentication!
            Please provide user and password via client
             fuel --user=user --password=pass [action]
            or modify "KEYSTONE_USER" and "KEYSTONE_PASS" in
            /etc/fuel/client/config.yaml""")
        except FuelClientException as exc:
            exit_with_error_or_traceback(exc)
        except Exception as exc:
            exit_with_error_or_traceback(exc)

    return wrapper


def get_error_body(error):
    try:
        error_body = json.loads(error.response.text)['message']
    except (ValueError, TypeError, KeyError):
        error_body = error.response.text

    return error_body
