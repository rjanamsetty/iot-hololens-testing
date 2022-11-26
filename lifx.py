import time

from lifxlan import LifxLAN

lifx = LifxLAN(1)


class Lifx:
    bright = 0

    def on(self):
        """
        Turns on all lights
        :return: None
        """
        lifx.set_power_all_lights("on", rapid=True)

    def off(self):
        """
        Turns off all lights
        :return: None
        """
        lifx.set_power_all_lights("off", rapid=True)

    def power_state(self):
        """
        Gets the new state of the first light in the LifxLAN object
        :return: the new power state of the first light as a string
        """
        devices = lifx.get_lights()
        return 'off' if devices[0].get_power() == 0 else "on"

    def set_brightness(self, brightness):
        """
        Sets the brightness of all lights to the given value
        :param brightness: the brightness value to set
        :return: None
        """
        self.bright = brightness
        devices = lifx.get_lights()
        for device in devices:
            device.set_brightness(brightness, rapid=True)
        time.sleep(0.5)

    def get_brightness(self):
        return self.bright

    # Toggles power state of all lights based on current state of the first light
    def toggle(self):
        """
        Toggles power state of all lights based on current state of the first light
        :return: the new, changed power state of the first light as a string
        """
        new_state = self.power_state()
        self.on() if self.power_state() == 'off' else self.off()
        return new_state


if __name__ == "__main__":
    lifx = Lifx()
    lifx.set_brightness(2500)
