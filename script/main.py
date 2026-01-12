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

    def CapitalizeNoSpace(self, word):
        return word.replace(" ", "").capitalize()

    def CreateFixture(self, **param_dict):
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
        amount = param_dict.get("Amount")
        template = param_dict.get("Template")
        fixture_group = param_dict.get("Group")
        fixture_id = param_dict.get("Id")

        def initPage(page_name, comp, t_params):
            # get the "Setting" page
            page = next((pg for pg in comp.customPages if pg.name == page_name), None)
            if page is None:
                page = comp.appendCustomPage(page_name)

            # create each float param if it doesn't exist yet
            for name in t_params:
                new_name = self.CapitalizeNoSpace(name)

                if not hasattr(comp.par, new_name):
                    par = page.appendFloat(new_name, label=name)

                    # TODO create min, max, default values for each parameter - maybe create a dictionary

            page = comp.customPages[page_name]
            for param in page:
                if param.label not in t_params:
                    comp.par[param.name].destroy()

        def initNetwork(comp):
            """generate network operator with op().create() or optionally copy an operator with the network already inside then I don't need this"""
            # create base network

        def initDefaultValues(comp, fixture_id, channels, **param_dict):
            """set default values for each created parameter"""

            footprint = channels.numRows - 1
            dmx_address = param_dict.get("Dmxstartaddress") + footprint * (
                fixture_id - 1
            )

            # TODO missing universe parameter
            defaults = {
                "Pan": 0.5,
                "Tilt": 0.5,
                "Madimmer": 1,
                "Group": param_dict.get("Group"),
                "Id": fixture_id,
                "DMXstartaddress": dmx_address,
                "Footprint": footprint,
            }

            for param, value in defaults.items():

                if comp.par[self.CapitalizeNoSpace(param)] is not None:
                    # print(comp, param, value, comp.par[self.CapitalizeNoSpace(param)])
                    comp.par[self.CapitalizeNoSpace(param)] = value

            # Group, ID, DMX Start Address from CreateFixture() Function

            # Footprint from template table length

        def initDmxChannels(comp, channels):
            """
            create all dmx channels in the constant CHOP of the fixture this CHOP will act as the starting naming point to match the names in the storage
            naming convention: fixture_name:dmxchannel.name
            """
            const = comp.op("const_channels")

            # reset CHOP channels
            const.par.name0.sequence.numBlocks = 1

            curChan = 0
            # build new CHOP channels and name them
            for channel in channels.col("Function")[1:]:
                channel_name = self.CapitalizeNoSpace(channel.val)
                pValue = f"const{curChan}value"
                pName = f"const{curChan}name"
                const.par[pValue] = 0
                const.par[pName] = f"{comp.name}:{channel_name}"
                curChan += 1

            # insert selection for parameterCHOP
            parCHOP = comp.op("par1")
            parameter_selection = ""
            renameto_selection = ""

            channels_page = next(
                (page for page in comp.customPages if page.name == "Channels"), None
            )

            for channel in channels_page.pars:
                parameter_selection += f"{channel.name} "
                renameto_selection += f"{comp.name}:{channel.name} "

            parCHOP.par.parameters = parameter_selection
            parCHOP.par.renameto = renameto_selection

        for num_fixture in range(1, amount + 1):
            fixture_name = f"{fixture_group}_{template}_{fixture_id}"
            if op(f"fixtures/{fixture_name}") is None:
                # fixture = op("fixtures").create(containerCOMP, fixture_name)
                fixture = op("fixtures").copy(op("base_network"), name=fixture_name)
                fixture.nodeX = fixture_group * 150
                fixture.nodeY = -num_fixture * 150
            else:
                fixture = op(f"fixtures/{fixture_name}")

            settings_list = ["Group", "ID", "DMX Start Address", "Footprint"]
            initPage(page_name="Settings", comp=fixture, t_params=settings_list)

            channels = op(f"fixture_templates/{template}")
            page_channels_list = [
                c.val
                for c in channels.col("Function")[1:]  # Skip header 'Function'
                if "Fine" not in c.val
            ]
            initPage(page_name="Channels", comp=fixture, t_params=page_channels_list)

            master_list = ["MA DIMMER"]
            initPage(page_name="Master", comp=fixture, t_params=master_list)

            initDefaultValues(fixture, fixture_id, channels, **param_dict)

            initDmxChannels(fixture, channels)

            # initNetwork(comp=fixture)
            fixture_id += 1

        # TODO once I create a fixture I need to update my rename CHOP and constant CHOPs that control my override CHOP

    def updateFixtures(self):
        """
        would be nice to have, still need to figure out how in what way I need this
        update the network by deleting all operators inside a network and then copy all the operators from base again
        """

    def ResetFixtureExpressions(self, operators):
        """
        once I set values manually via the fixture settings
        I want to reconnect them to the osc input and make
        the expressions active
        """

        for op in operators.children:
            # Check if 'Channels' page exists by name
            channels_page = next(
                (page for page in op.customPages if page.name == "Channels"), None
            )
            if channels_page is not None:
                # print(f"Channels page found on {op}")
                # Now iterate parameters on that page (or use op.par for direct access)
                channels_pars = [
                    par for par in op.customPars if par.page.name == "Channels"
                ]
                for channel in channels_pars:
                    print(channel.name)
                    # insert a string as expression
                    expression = f"op('in1')[f'{{me.name}}:{{me.curPar.name}}']"
                    op.par[channel.name].mode = ParMode.EXPRESSION
                    op.par[channel.name].expr = expression
