import argparse
import datetime
import os
import re
import shutil

import packaging.version

from pip_bump_requirements.pypi import PyPiApi


class Bump(object):
    pypiapi = PyPiApi()

    @staticmethod
    def parse_package(package):
        package_pattern = r'''^(?P<package_name>[a-zA-Z0-9.\-_]+)==(?P<package_version>[a-zA-Z0-9.\-_]+)$'''
        package_match = re.match(package_pattern, package)
        if package_match:
            package_dict = {
                "package_name": package_match.groupdict()['package_name'],
                "package_version": package_match.groupdict()['package_version']
            }
            return package_dict
        return None

    def get_project_parsed_versions(self, project, release=True):
        project_versions = []
        release_pattern = r'''^[0-9.]+$'''
        project_json = self.pypiapi.project(project)
        versions = project_json.get('releases', {})
        for version in versions:
            parsed_version = packaging.version.parse(version)
            if release is True:
                if re.match(release_pattern, version):
                    project_versions.append((parsed_version, version))
            else:
                project_versions.append((parsed_version, version))
        return project_versions

    def get_newset_project_release(self, project):
        project_parsed_versions = self.get_project_parsed_versions(project)
        latest_version = None
        for project_parsed_version in project_parsed_versions:
            if latest_version is None:
                latest_version = project_parsed_version
            else:
                if project_parsed_version[0] > latest_version[0]:
                    latest_version = project_parsed_version
        return latest_version

    def bump_versions(self, requirements_in_path):
        bumped_requirements = []
        bumps = False
        with open(requirements_in_path, 'rt') as requirements_in_path_fo:
            for line in requirements_in_path_fo:
                line = line.strip()
                package_dict = self.parse_package(line)
                if isinstance(package_dict, dict):
                    current_release_versioned = packaging.version.parse(package_dict['package_version'])
                    newset_project_release = self.get_newset_project_release(package_dict['package_name'])
                    if (
                            isinstance(
                                current_release_versioned,
                                (packaging.version.LegacyVersion, packaging.version.Version))
                            and
                            isinstance(
                                newset_project_release[0],
                                (packaging.version.LegacyVersion, packaging.version.Version))
                    ):
                        if newset_project_release[0] > current_release_versioned:
                            print(f'Bump {package_dict["package_name"]} from {package_dict["package_version"]}'
                                  f' to {newset_project_release[1]}')
                            bumped_requirements.append(f'{package_dict["package_name"]}=={newset_project_release[1]}')
                            bumps = True
                        else:
                            print(f'No Bump {package_dict["package_name"]} from {package_dict["package_version"]}'
                                  f' to {newset_project_release[1]}')
                            bumped_requirements.append(line)
                    else:
                        print(f'Cannot parse {current_release_versioned} or {newset_project_release[0]}'
                              f'using packaging.version.parse')
                        bumped_requirements.append(line)
                else:
                    print(f'package_dict {package_dict} is not a dict but {type(package_dict)}')
                    bumped_requirements.append(line)
        return bumps, bumped_requirements

    def bump(self, requirements_in_path):
        bumps, bumped_requirements = self.bump_versions(requirements_in_path)
        if bumps is True:
            backup_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%m-%S')
            backup_filename = f'{requirements_in_path}.{backup_time}'
            shutil.move(requirements_in_path, backup_filename)
            print(f'backuped up {requirements_in_path} to {backup_filename}.')
            with open(requirements_in_path, 'wt') as requirements_in_path_fo:
                for bumped_requirement in bumped_requirements:
                    requirements_in_path_fo.write(f'{bumped_requirement}{os.linesep}')


def main():
    parser = argparse.ArgumentParser(description='Bump requirements.txt versions')
    parser.add_argument('-r', action='store', dest='requirements_in_path', required=True, type=str,
                        help='/path/to/requirements.in')
    args = parser.parse_args()

    requirements_in_path = args.requirements_in_path

    if os.path.isfile(requirements_in_path):
        print(f'{requirements_in_path} is a file.')
        bump = Bump()
        bump.bump(requirements_in_path)
    else:
        print(f'{requirements_in_path} is not a file.')
