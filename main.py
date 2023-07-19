from iFlask_app.controller import Controller


def main() -> None:
    """Run the iFlask application."""

    controller = Controller()
    controller.reload()
    controller.view.connect_to_esp32()
    controller.run()
    controller.view.disconnect_from_esp32()


if __name__ == "__main__":
    main()
