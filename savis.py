#!/usr/bin/env python3

import argparse
import logging
import pathlib
import os
import sys
import ast
import collections
import jinja2


logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(message)s')
Field = collections.namedtuple('Field', ('name', 'data_type', 'extra'))


class readable_dir(argparse.Action):
    def __call__(self, parser, namespace, dir_, option_string=None):
        if not os.path.isdir(dir_) or not os.access(dir_, os.R_OK):
            print(dir_ + ': nonexistant or inaccessible directory', file=sys.stderr)
            sys.exit(1)
        setattr(namespace, self.dest, pathlib.Path(dir_))


def get_member_names(node):
    if not hasattr(node, 'body'):
        return
    for member in node.body:
        if not hasattr(member, 'targets') or not member.targets:
            continue
        for target in member.targets:
            yield target.id


def is_primary_column_def(member):
    kws = member.value.keywords
    if not kws:
        return False
    return [x.value.value for x in kws if x.arg == 'primary_key'][0]


def get_model_fields(node):
    if not hasattr(node, 'body'):
        return

    for member in node.body:
        if not isinstance(member, ast.Assign):
            continue

        if not isinstance(member.value, ast.Call):
            continue

        v = member.value
        if v.func.id != 'Column' or not v.args:
            continue

        extra = {}
        if is_primary_column_def(member):
            extra['primary'] = True

        a = v.args[0]
        if isinstance(a, ast.Call):
            data_type = a.func.id
        elif isinstance(a, ast.Name):
            data_type = a.id
        if data_type == 'ForeignKey':
            foreign_name = a.args[0].value.id
            extra['foreign'] = foreign_name
            data_type += '(' + foreign_name + ')'
        yield Field(member.targets[0].id, data_type, extra)


def find_models(node):
    if isinstance(node, ast.ClassDef):
        if '__tablename__' in get_member_names(node):
            yield node

    if hasattr(node, 'body'):
        for child in node.body:
            yield from find_models(child)


def describe(model, output_format):
    if output_format == 'human':
        print(model.name)
        for entry in get_model_fields(model):
            print('\t', entry)
    else:
        template = (
            '[{{ model_name }}]\n'
            '{% for f in fields -%}\n'
            '    {% if f.extra.primary %}*{% endif %}{{ f.name }} {label:"{{ f.data_type }}"}\n'
            '{% endfor %}\n\n'
        )

        fields = list(get_model_fields(model))
        print(jinja2.Template(template).render(model_name=model.name, fields=fields))
        foreign_keys = []
        for f in fields:
            if 'foreign' in f.extra:
                foreign_keys.append((f.extra['foreign'], model.name))
        return foreign_keys


def describe_foreign_keys(fks, output_format):
    for fk in fks:
        print(fk[0], '1--1', fk[1])


def main(input_dir, exclude, output_format):
    for file_ in input_dir.glob('**/*.py'):
        if exclude is not None and file_.match(exclude):
            continue
        logging.info(f'Processing {file_}')
        with open(file_) as f:
            root = ast.parse(f.read(), file_)
            models = find_models(root)
            foreign_keys = []
            for model in models:
                foreign_keys.extend(describe(model, output_format))
            describe_foreign_keys(foreign_keys, output_format)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('input_dir', action=readable_dir)
    arg_parser.add_argument('-e', '--exclude')
    arg_parser.add_argument('-o', '--output', default='human', choices=('human', 'md'))
    args = arg_parser.parse_args()
    main(args.input_dir, args.exclude, args.output)
