import pb

TEST_FILE = "test.pb.gz"


def main():
    messages = [{"device": {}, "lat": 2.314141, "lon": 5.66523423}]
    print(messages)
    pb.deviceapps_xwrite_pb(messages, TEST_FILE)

    unpacked = list(pb.deviceapps_xread_pb(TEST_FILE))
    print(unpacked)


if __name__ == "__main__":
    main()
