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
        # optimize OSC messaging and use 
    def saveStorageExt(self):
        """
        TODO upon storing fixture data save the storage to a new file
        """

    def RecallStorage(self, val, channel):
        """

        upon selecting a preset from the scene selector
        send OSC messages that update the PCs OSCIn and
        TouchOSCs Input
        manage if bank 1 or 2 is selected and therefore
        send to the correct bank
        TODO it would be nice to filter for certain parameters
        TODO currently pulls dimmer values from table_storage(deprecated) - change to new storage location
        """

        if channel.index == 0:
            bank = "OSC1"
        else:
            bank = "OSC2"

        # create a client_tosc that sends to IP 127.0.0.1, port 8000
        client_tosc = udp_client.SimpleUDPClient("192.168.178.105", 8001)
        client_local = udp_client.SimpleUDPClient("192.168.178.107", 10000)

        preset = "table_storage"

        for item in range(op(preset).numRows)[1:]:
            # Get the target parameter name and value from the table
            osc_address = op(preset)[item, bank].val
            osc_address = "/" + osc_address
            par_val = float(
                op(preset)[item, int(val + 6)].val
            )  # offset by 6 to get in range of stored parameters

            try:
                client_tosc.send_message(f"{osc_address}", par_val)
                client_local.send_message(f"{osc_address}", par_val)
                print(f"Sent value {par_val} to {osc_address}")

            except Exception as e:
                # handle/log and continue the loop so one failure doesn't abort the whole routine
                print(f"Failed to send OSC to {osc_address}: {e}")

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
        """
        comp = op("container2")  # replace with your component

        # get the "Setting" page
        page = next((pg for pg in comp.customPages if pg.name == "Custom"), None)
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
        page = next((pg for pg in comp.customPages if pg.name == "Custom"), None)
        if page is None:
            page = comp.appendCustomPage("Custom")

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

    def resetFixtureExpressions(self):
        """
        TODO once I set values manually via the fixture settings
        I want to reconnect them to the osc input and make
        the expressions active
        """
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

    def Test(self):
        print("test")
