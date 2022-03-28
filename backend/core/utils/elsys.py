import binascii

TYPE_TEMP = 0x01  # temp 2 bytes -3276.8°C -->3276.7°C
TYPE_RH = 0x02  # Humidity 1 byte  0-100%
TYPE_ACC = 0x03  # acceleration 3 bytes X,Y,Z -128 --> 127 +/-63=1G
TYPE_LIGHT = 0x04  # Light 2 bytes 0-->65535 Lux
TYPE_MOTION = 0x05  # No of motion 1 byte  0-255
TYPE_CO2 = 0x06  # Co2 2 bytes 0-65535 ppm
TYPE_VDD = 0x07  # VDD 2byte 0-65535mV
TYPE_ANALOG1 = 0x08  # VDD 2byte 0-65535mV
TYPE_GPS = 0x09  # 3bytes lat 3bytes long binary
TYPE_PULSE1 = 0x0A  # 2bytes relative pulse count


def bin16dec(value):
    num = value & 0xFFFF
    if 0x8000 & num:
        num = -(0x010000 - num)
    return num


def bin8dec(value):
    num = value & 0xFF
    if 0x80 & num:
        num = -(0x0100 - num)
    return num


def decode_elsys_payload(data):
    obj = {}

    i = 0
    while i < len(data):
        val = data[i]

        if val == TYPE_TEMP:
            temp = (data[i + 1] << 8) | (data[i + 2])
            temp = bin16dec(temp)
            obj['temperature'] = temp / 10
            i += 2
        elif val == TYPE_RH:
            rh = data[i + 1]
            obj['humidity'] = rh
            i += 1
        elif val == TYPE_ACC:
            obj['x'] = bin8dec(data[i + 1])
            obj['y'] = bin8dec(data[i + 2])
            obj['z'] = bin8dec(data[i + 3])
            i += 3
        elif val == TYPE_LIGHT:
            light = (data[i + 1] << 8) | (data[i + 2])
            obj['light'] = light
            i += 2
        elif val == TYPE_MOTION:
            motion = data[i + 1]
            obj['motion'] = motion
            i += 1
        elif val == TYPE_CO2:
            co2 = (data[i + 1] << 8) | (data[i + 2])
            obj['co2'] = co2
            i += 2
        elif val == TYPE_VDD:
            vdd = (data[i + 1] << 8) | (data[i + 2])
            obj['vdd'] = vdd
            i += 2
        elif val == TYPE_ANALOG1:
            analog1 = (data[i + 1] << 8) | (data[i + 2])
            obj['analog1'] = analog1
            i += 2
        elif val == TYPE_GPS:
            obj['lat'] = (data[i + 1] << 16) | (data[i + 2] << 8) | (data[i + 3])
            obj['long'] = (data[i + 4] << 16) | (data[i + 5] << 8) | (data[i + 6])
            i += 6
        elif val == TYPE_PULSE1:
            pulse1 = (data[i + 1] << 8) | (data[i + 2])
            obj['pulse1'] = pulse1
            i += 2
        else:
            logging.warning(f'Unsupported value {val}')

        i += 1  # compensate for first byte

    return obj


if __name__ == '__main__':
    payload = binascii.unhexlify('0100CD')
    decoded = decode_elsys_payload(payload)
    print(decoded)
