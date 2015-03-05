#    Copyright 2015 Mirantis, Inc.
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


def get_display_data_single(fields, data):
    """Performs slice of data by set of given fields

    :param fields: Iterable containing names of fields to be retrieved
                   from data
    :param data:   Collection of JSON objects representing some
                   external entities

    :return:       list containing the collection of values of the
                   supplied attributes.

    """
    result = []

    for field in fields:
        val = data.get(field)
        if val == {} or val == []:
            val = 'Empty'

        if val is not None:
            result.append(val)

    return result


def get_display_data_mult(fields, data):
    """Performs slice of data by set of given fields for multiple objects."""

    return [get_display_data_single(fields, elem) for elem in data]


def str_to_array(input_str, separator, items_type):
    """Converts a string into a list of items

    :param input_str:  str, containing items, separated by a symbol
    :param separator:  The symbol, that separates items in the string
    :param items_type: Type of the items in the string.
    :return:           list, containing items of the specified type


    """
    try:
        return [items_type(it) for it in input_str.split(separator)]
    except ValueError:
        msg = 'All items in "{st}" are expected to be {t}'.format(st=input_str,
                                                                  t=items_type)
        raise ValueError(msg)
