# -*- coding: utf-8 -*-

import centreonapi.webservice.configuration.common as common
import bs4
from centreonapi.webservice import Webservice


class Command(common.CentreonObject):

    def __init__(self, properties):
        self.webservice = Webservice.getInstance()
        self.__clapi_action = 'CMD'
        self.id = properties.get('id')
        self.name = properties.get('name')
        self.line = self._build_command_line(properties.get('line'))
        self.type = properties.get('type')

    @staticmethod
    def _build_command_line(line):
        if line:
            if isinstance(line, list):
                command_line = "|".join(line)
            else:
                command_line = line
            command_line_soup = bs4.BeautifulSoup(command_line, "html.parser")
            command_line_soup = str(command_line_soup).replace('<br/>', '\n')
            command_line_soup = str(command_line_soup).replace('&amp;', '&')
            return str(command_line_soup)
        else:
            return ""

    def setparam(self, name, value):
        """
        Set specific param for a command

        :param name: param name
        :param value: param value
        :return:
        """
        values = [
            self.name,
            name,
            value
        ]
        return self.webservice.call_clapi('setparam',
                                          self.__clapi_action,
                                          values)


class Commands(common.CentreonDecorator, common.CentreonClass):
    """
    Centreon Web Command object
    """
    def __init__(self):
        super(Commands, self).__init__()
        self.commands = {}
        self.__clapi_action = "CMD"

    def __contains__(self, name):
        return name in self.commands.keys()

    def __getitem__(self, name):
        if not self.commands:
            self.list()
        if name in self.commands.keys():
            return True, self.commands[name]
        else:
            return False, None

    def _refresh_list(self):
        self.commands.clear()
        state, command = self.webservice.call_clapi(
                            'show',
                            self.__clapi_action)
        if state and len(command['result']) > 0:
            for c in command['result']:
                command_obj = Command(c)
                self.commands[command_obj.name] = command_obj

    @common.CentreonDecorator.pre_refresh
    def list(self):
        """
        List all commands

        :return: dict: All Centreon command
        """
        return self.commands

    @common.CentreonDecorator.post_refresh
    def add(self, cmdname, cmdtype, cmdline, post_refresh=True):
        """
        Add a command

        :param cmdname: command name
        :param cmdtype: command type (check, notif, misc or discovery)
        :param cmdline: System command line that will be run on execution
        :param post_refresh: boolean: refresh Commands object
        :return:
        """
        values = [
            cmdname,
            cmdtype,
            cmdline
        ]
        return self.webservice.call_clapi(
            'add',
            self.__clapi_action,
            values)

    @common.CentreonDecorator.post_refresh
    def delete(self, command, post_refresh=True):
        """
        Delete a command
        :param command: command name
        :param post_refresh: boolean: refresh Commands object
        :return:
        """
        value = str(common.build_param(command, Command)[0])
        return self.webservice.call_clapi('del', self.__clapi_action, value)
