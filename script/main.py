from pythonosc import udp_client
import datetime


class Main:
    def __init__(self, ownerCOMP):
        self.ownerCOMP = ownerCOMP

        # shortcut to look up operators relative to this COMP
        oop = self.ownerCOMP.op
        self.oop = oop

    def SavePreset(self):
        """
        Save every preset in a different DAT with corresponding
        parameter names, values and fixture path.
        The created preset tables will then be merged and sorted
        accordingly ensuring that when new fixtures are created
        the presets dont get messed up.
        """
        print("Storing...")
        source = op("storage/parameters")
        store_pos = op("storage_pos")
        preset_name = "preset" + str(int(store_pos[0] + 1))

        col_selection = ["name", "value"]

        storage = op("storage")
        target = storage.op(preset_name)

        try:
            """check for existing table"""
            target.valid
            self._fillPresetTable(target, source, col_selection, preset_name)
            print(f"preset existed and overwriting {preset_name}")
        except Exception as e:
            """create table if it doesn't exist"""
            new_table = storage.create(tableDAT, preset_name)

            # delay initialization 60 frames
            run(
                self._initPresetTable(new_table, source, col_selection, preset_name),
                delayFrames=60,
            )
            print("new preset table created")

    def _initPresetTable(self, target, source, col_selection, preset_name):
        """Called delayed: set rows/cols and fill."""
        try:
            merge = op("storage/merge1")

            target.par.fill = 1
            target.viewer = 1
            target.par.rows = source.numRows
            target.par.cols = len(col_selection)
            target.outputConnectors[0].connect(merge)
            target.nodeY = target.digits * -150
            self._fillPresetTable(target, source, col_selection, preset_name)

            print(f"Initialized table {preset_name}- filling table...")
        except Exception as e:
            print(f"Couldn't initialize table - Exception: \n{e}")

    def _fillPresetTable(self, target, source, col_selection, preset_name):
        """Copy values from source to target."""
        try:
            for col in range(source.numCols):
                if source[0, col] in col_selection:
                    for row in range(source.numRows):
                        target[row, col] = source[row, col]
            target[0, "value"] = preset_name
            self._savePresetLocally(target)

            print(f"filled table at {preset_name}. Saving locally...")
        except Exception as e:
            print(f"Couldn't fill table - Exception: \n{e}")

    def _savePresetLocally(self, preset_name):
        """
        Save preset tables locally and create unique files to
        recover previous values
        example file path: Backup/fixtureData/datout.0.csv
        """
        try:
            fileout = op("storage/fileout1")
            preset_name.outputConnectors[0].connect(fileout)
            # construct ouput file path and name
            folder_location = "Backup/fixtureData/"

            dt_now = datetime.datetime.now()
            time = dt_now.strftime("-%Y%m%d-%H-%M-%S")
            file_ext = ".dat"
            file_path = folder_location + preset_name.name + time + file_ext

            fileout.par.file = file_path
            fileout.par.write.pulse()

            preset_name.par.file = file_path

            print("saved preset locally - sending feedback")
        except Exception as e:
            print(f"Couldn't save table locally - Exception: \n{e}")

    def _sendSaveFeedback(self):
        """
        TODO upon saving parameters send feedback to textport,
        UI and TouchOSC
        """
        # optimize OSC messaging and use the general osc module
        # with different targets and functionalities

    def sendOSC(self, osc_address, osc_val):
        client_tosc = udp_client.SimpleUDPClient("192.168.178.105", 8001)
        client_local = udp_client.SimpleUDPClient("192.168.178.107", 10000)

        try:
            client_tosc.send_message(address=osc_address, value=osc_val)
            client_local.send_message(address=osc_address, value=osc_val)
        except Exception as e:
            print(f"failed sending osc message with error:", e)

    """
    Override CHOP takes all values from different sources (TouchOSC, UI, preload section from storage)
    the single values that changes last will be selected from the different input CHOPs
    changes will be synced across the different UI panels upon loading presets or at the end of wiggled faders
    """

    def LoadPreset(self, val, channel):
        """
        trigger:
            upon selecting a preset from the TouchOSC scene selector the chopexecDAT ce_radio_bank will trigger this function
        function:
            send OSC messages that updates the PCs OSCIn and
            TouchOSCs Dimmer Faders
            manage if bank 1 or 2 is selected and therefore
            send to the correct bank

        TODO it would be nice to filter for certain parameters
        """

        dimmer_data = "storage/dimmer_data"
        bank = channel.index + 1
        preset = f"preset{int(val + 1)}"

        print(bank, preset)

        for dimmer in range(op(dimmer_data).numRows)[1:]:
            # Get the target parameter name and value from the table
            osc_address = f"/grid{bank}/{dimmer}"
            par_val = float(op(dimmer_data)[dimmer, preset].val)
            print(osc_address, par_val)
            self.sendOSC(osc_address, par_val)

    def createFixtures(self):
        """
        TODO programmatically create fixtures from preset
        create parameters for:
            dimmer
            colors
            pan/tilt
            gobo
        create settings:
            dmx address
            footprint
        create master parameters:
            master dimmer
        """
        comp = op("container2")  # replace with your component

        # get the "Setting" page
        page = next((pg for pg in comp.customPages if pg.name == "Settings"), None)
        if page is None:
            page = comp.appendCustomPage("Settings")

        settingList = ["DMX Address", "Footprint"]

        # create each float param if it doesn't exist yet
        for name in settingList:
            label = name.capitalize()
            new_name = label.replace(" ", "")
            print
            if not hasattr(comp.par, new_name):
                par = page.appendFloat(new_name, label=name)

        # get the "Custom" page (create it if it doesn't exist)
        page = next((pg for pg in comp.customPages if pg.name == "Parameters"), None)
        if page is None:
            page = comp.appendCustomPage("Parameters")

        # TODO this list should be pulled from locally stored preset tables,
        # add info for 8-bit or 16-bit values (FINE channels maybe) - don't create 2 fader in the parameter page for that section but the dmx channels inside the fixture
        # create a selector that pulls all the 16 bit floats and create two seperate dmx channels and replace them in the master chain
        # define your float parameters: name, label, default, min, max
        chanList = [
            "CYAN",
            "MAGENTA",
            "YELLOW",
            "CTO",
            "COLOR WHEEL",
            "STROBE EFFECT",
            "DIMMER",
            "DIMMER FINE",  # 8
            "IRIS",
            "ROTATING GOBO CHANGE",
            "GOBO ROTATION",
            "FINE GOBO ROTATION",  # 12
            "PRISM INSERTION",
            "PRISM ROTATION",
            "ANIMATION WHEEL INSERTION",
            "ANIMATION WHEEL ROTATION",
            "FROST",
            "FOCUS",
            "ZOOM",
            "BLADE 1 MOVEMENT",
            "BLADE 1 SWIVELLING",
            "BLADE 2 MOVEMENT",
            "BLADE 2 SWIVELLING",
            "BLADE 3 MOVEMENT",
            "BLADE 3 SWIVELLING",
            "BLADE 4 MOVEMEN",
            "BLADE 4 SWIVELLING",
            "FRAME ROTATION",
            "FRAME MACROS",
            "FRAME MACRO SPEED",
            "PAN",
            "PAN FINE",  # 32
            "TILT",
            "TILT FINE",  # 34
            "RESET",
            "FUNCTION",
        ]

        # create each float param if it doesn't exist yet
        for name in chanList:
            label = name.capitalize()
            new_name = label.replace(" ", "")
            print
            if not hasattr(comp.par, new_name):
                par = page.appendFloat(new_name, label=label)

        # TODO create master page

        # TODO once I create a fixture I need to update my rename CHOP and constant CHOPs that control my override CHOP

    def resetFixtureExpressions(self):
        """
        TODO once I set values manually via the fixture settings
        I want to reconnect them to the osc input and make
        the expressions active
        """

        # this scenario needs to be triggered when I change the fixture values manually
        # could be triggered when I save presets or recall presets - or explicitely create a CLEAR button

        target = op("fixture_data")
        source = op("colorScene")

        """when constant changes are applied to the colors reference a pixel from the source to the corresponding path"""
        for i in range(1, target.numRows):
            operator = op(target[i, "path"])
            param = str(target[i, "name"])
            print(operator, param, type(param))
            param = param.split(":", 1)[-1]
            print(param, type(param))

            operator.pars(param)[0].mode = ParMode.EXPRESSION
            operator.pars(param)[0].expr = f"op('colorScene')[0][{i-1}]"
