import dataclasses
from typing import Protocol
from unittest import TestCase

from automat import TypeMachineBuilder


class SwitchProtocol(Protocol):

    def flip(self) -> None:
        "Toggle the switch to its opposite"

    def flip_with_exception(self) -> None:
        "Toggle the switch to its opposite and then raise an exception"

    def is_on(self) -> bool:
        "Report if switch is in on position"


@dataclasses.dataclass
class SwitchController:
    status: bool

    def __init__(self):
        self.status = False

    def toggle(self):
        self.status = not self.status

    def get_status(self):
        return self.status

@dataclasses.dataclass
class Devices:
        switch: SwitchController


builder = TypeMachineBuilder(SwitchProtocol, SwitchController)

off = builder.state('off')
on = builder.state('on')

@off.upon(SwitchProtocol.flip).to(on)
def flip_switch_on(controller: SwitchController, devices: Devices):
    devices.switch.toggle()

@on.upon(SwitchProtocol.flip).to(off)
def flip_switch_off(controller: SwitchController, devices: Devices):
    devices.switch.toggle()

class OperationException(Exception):
    pass

@off.upon(SwitchProtocol.flip_with_exception).to(on)
def flip_switch_on_exception(controller: SwitchController, devices: Devices):
    devices.switch.toggle()
    raise OperationException()

@on.upon(SwitchProtocol.flip_with_exception).to(off)
def flip_switch_off_exception(controller: SwitchController, devices: Devices):
    devices.switch.toggle()
    raise OperationException()

@on.upon(SwitchProtocol.is_on).loop()
def report_on(controller: SwitchController, devices: Devices):
    return devices.switch.get_status()

@off.upon(SwitchProtocol.is_on).loop()
def report_on(controller: SwitchController, devices: Devices):
    return devices.switch.get_status()

# With this kind of implementation, it should be possible to put the machine into a bad state.

switchFactory = builder.build()

class StateTests(TestCase):
    def test_goodflip(self):
        switch = switchFactory(Devices(SwitchController()))
        self.assertFalse(switch.is_on())
        switch.flip()
        self.assertTrue(switch.is_on())

    def test_exception_flip(self):
        """
        When an exception is raised, the internal state of the machine should not change.
        """
        switch = switchFactory(Devices(SwitchController()))
        self.assertFalse(switch.is_on())
        with self.assertRaises(OperationException) as cm:
            switch.flip()
            self.assertFalse(switch.is_on())