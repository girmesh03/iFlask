"""The main module of the iFlask application."""

from iFlask_app.controller import Controller


def main() -> None:
    """Run the iFlask application."""

    controller = Controller()
    controller.reload()
    controller.view.connect_to_esp32()
    controller.run()
    controller.view.disconnect_from_esp32()
    controller.reset_default_config()


if __name__ == "__main__":
    """Run the iFlask application."""
    main()
