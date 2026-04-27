from ms_app.app import main

if __name__ == "__main__":
    # # For Toga app debugging
    # import sys
    #
    # if not sys.modules["__main__"].__package__:
    #     import os
    #
    #     package = os.path.basename(os.path.dirname(__file__))
    #     sys.modules["__main__"].__package__ = package

    main().main_loop()

