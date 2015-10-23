# -*- coding: utf-8 -*-
import os
import sys
import nixops.util

from nixops.backends import MachineDefinition, MachineState
from nixops.util import attr_property, create_key_pair


class NoneDefinition(MachineDefinition):
    """Definition of a trivial machine."""

    @classmethod
    def get_type(cls):
        return "none"

    def __init__(self, xml):
        MachineDefinition.__init__(self, xml)
        self._target_host = xml.find("attrs/attr[@name='targetHost']/string").get("value")


class NoneState(MachineState):
    """State of a trivial machine."""

    @classmethod
    def get_type(cls):
        return "none"

    target_host = nixops.util.attr_property("targetHost", None)
    _ssh_private_key = attr_property("none.sshPrivateKey", None)
    _ssh_public_key = attr_property("none.sshPublicKey", None)

    def __init__(self, depl, name, id):
        MachineState.__init__(self, depl, name, id)

    @property
    def resource_id(self):
        return self.vm_id

    def get_physical_spec(self):
        return {
            ('config', 'users', 'extraUsers', 'root', 'openssh',
             'authorizedKeys', 'keys'): [self._ssh_public_key]
        } if self._ssh_public_key else {}

    def create(self, defn, check, allow_reboot, allow_recreate):
        assert isinstance(defn, NoneDefinition)
        self.set_common_state(defn)
        self.target_host = defn._target_host

        if not self.vm_id:
            self.log_start("generating new SSH keypair...")
            key_name = "NixOps client key for {0}".format(self.name)
            self._ssh_private_key, self._ssh_public_key = \
                create_key_pair(key_name=key_name)
            self.log_end("done.")
            self.vm_id = "nixops-{0}-{1}".format(self.depl.uuid, self.name)

    def get_ssh_name(self):
        assert self.target_host
        return self.target_host

    def get_ssh_private_key_file(self):
        if self._ssh_private_key_file:
            return self._ssh_private_key_file
        else:
            return self.write_ssh_private_key(self._ssh_private_key)

    def get_ssh_flags(self):
        if self.vm_id and self.cur_toplevel:
            return ["-o", "StrictHostKeyChecking=no",
                    "-i", self.get_ssh_private_key_file()]
        return []

    def _check(self, res):
        if not self.vm_id:
            res.exists = False
            return
        res.exists = True
        res.is_up = nixops.util.ping_tcp_port(self.target_host, self.ssh_port)
        if res.is_up:
            MachineState._check(self, res)

    def destroy(self, wipe=False):
        # No-op; just forget about the machine.
        return True
