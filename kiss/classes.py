#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""KISS Core Classes."""

__author__ = 'Greg Albrecht W2GMD <gba@onbeep.com>'
__copyright__ = 'Copyright 2013 OnBeep, Inc.'
__license__ = 'Apache 2.0'


import logging

import serial

import kiss.constants
import kiss.util


class KISS(object):

    """KISS Object Class."""

    logger = logging.getLogger(__name__)
    logger.setLevel(kiss.constants.LOG_LEVEL)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(kiss.constants.LOG_LEVEL)
    formatter = logging.Formatter(kiss.constants.LOG_FORMAT)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.propagate = False

    def __init__(self, port, speed):
        self.port = port
        self.speed = speed
        self.serial_int = None  # TODO Potentially very f*cking unsafe.

    def start(self):
        """
        Initializes the KISS device and commits configuration.
        """
        self.logger.debug('start()')
        self.serial_int = serial.Serial(self.port, self.speed)
        self.serial_int.timeout = kiss.constants.SERIAL_TIMEOUT

        # http://en.wikipedia.org/wiki/KISS_(TNC)#Command_Codes
        kiss_config = {}  # TODO Yes, this isn't complete.
        for setting in ['TX_DELAY', 'PERSISTENCE', 'SLOT_TIME', 'TX_TAIL',
                        'FULL_DUPLEX']:
            if kiss_config.get(setting):
                self.write_setting(kiss_config[setting])

    def write_setting(self, setting):
        """
        Writes KISS Command Codes to attached device.

        :param setting: KISS Command Code to write.
        """
        return self.serial_int.write(
            kiss.constants.FEND +
            kiss.constants.FULL_DUPLEX +
            kiss.util.escape_special_codes(setting) +
            kiss.constants.FEND
        )

    def read(self, callback=None):
        """
        Reads data from KISS device.

        :param callback: Callback to call with decoded data.
        """
        read_buffer = ''
        while 1:
            read_data = self.serial_int.read(kiss.constants.READ_BYTES)

            waiting_data = self.serial_int.inWaiting()

            if waiting_data:
                read_data = ''.join([
                    read_data, self.serial_int.read(waiting_data)])

            if read_data:
                frames = []

                split_data = read_data.split(kiss.constants.FEND)
                len_fend = len(split_data)
                self.logger.debug('len_fend=%s', len_fend)

                # No FEND in frame
                if len_fend == 1:
                    read_buffer = ''.join([read_buffer, split_data[0]])
                # Single FEND in frame
                elif len_fend == 2:
                    # Closing FEND found
                    if split_data[0]:
                        # Partial frame continued, otherwise drop
                        frames.append(''.join([read_buffer, split_data[0]]))
                        read_buffer = ''
                    # Opening FEND found
                    else:
                        frames.append(read_buffer)
                        read_buffer = split_data[1]
                # At least one complete frame received
                elif len_fend >= 3:
                    for i in range(0, len_fend - 1):
                        _str = ''.join([read_buffer, split_data[i]])
                        if _str:
                            frames.append(_str)
                            read_buffer = ''
                    if split_data[len_fend - 1]:
                        read_buffer = split_data[len_fend - 1]

                # Loop through received frames
                for frame in frames:
                    if len(frame) and ord(frame[0]) == 0:
                        with open('full_frame.log', 'a+') as full_frame:
                            full_frame.write(frame[1:] + '\n')

                        self.logger.info('frame=%s', frame)
                        if callback:
                            callback(frame)

    def write(self, frame):
        """
        Writes frame to KISS device.

        :param frame: Frame to write.
        """
        return self.serial_int.write(''.join([
            kiss.constants.FEND,
            kiss.constants.DATA_FRAME,
            kiss.util.escape_special_codes(frame),
            kiss.constants.FEND
        ]))
