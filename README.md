# TdLightingdesign-ich-bin-mir-selber-fremd-geworden
creating a lighting environment that is portable and minimalistic yet able to do complex stuff: combines lighting, visuals, TouchOSC interface, managing presets, CHOP DMX

## commment on stability and  feature staging
- creating fixtures and outputting dmx works really well
- loading presets is also very stable
- parameter UI elements are quite wonky as are the updateUI scripts - currently disabled

## TODOs urgent   
- patch Gera show
- test: after setting windows machine to sleep the dmxout CHOP seems to have problems with sending dmx packages
- 
- problem with ui_bank buttons: sometimes can't select first button

## TODOs
- collect example photos for "fremd geworden" scenes
- UI for setting up parameters:
    - Moving Heads
- presets and groups
    - fixture selector
    - grouping fixtures and controlling them simultaneously
    - presets for Color, Position, FX
- rework TouchOSC patch with grid:text and auto generating and naming faders
- optimize projector fading from off to on - projector needs a little time to turn on which results in a brightness jump when it turns on 
- park fixtures
- create a fixture renaming function that also updates the storage table
- create overview plan from network in README.md
- rework network to select visuals - create a projector fixture but don't send it to the dmx channels but it should still populate into the UI
- optimize save function to only store/update changed values to change processing time
- create OSC feedback for:
    - save function
    - fog machine lock
- update all UI inputs based on the last one that changed (partially solved)
    - use mapping table
- create update script to update select operators

### ideas
- sometimes triggering a python script is heavy on the cpu and results in frame drops
    - some functions don't need to executed realtime
    - looping through the task and setting an increasin delayFrame could help like
    for i in list:
        run(script, delayFrame=i)

## Documentation

### settings
- ui element for settings lets you
    - save presets
    - lock fog machine
    - set ip addresses
    - control Grandmaster level
    - 
### createFixtures
if there are no "Dimmer" or "Intensity" in dmxfunctions a virtual one will be created
TODO virtual dimmer should only affect color parameters - fixtures with strobe need to be selected carefully

### storage
- select operators from the storage/parameters DAT will be used throughout the network which creates loops
    - since all values in null2 are constant locking it solves the problem
    - changes happen only when there are more fixtures created - adding an update script to the CreateFixture() function from main.py could unlock and re-lock null2

### load Banks
- managed via buttons and faders from UI or TouchOSC
    - buttons in two banks load the presets directly from the storage table
    - a bank_fader crossfades between banks 

### TD Lighting UI
- Master Fader
    - lets you fade between banks with preloaded scenes
- Dimmer page
    - radio buttons for selecting scenes in two preload banks
    - auto-populates dimmer faders based on how many fixtures with dimmers there are
- Save page
    - save button
    - feedback
    - text editor to see errors on the fly
- Moving Head page (yet to be developed)
    - select a moving head from a radio button field
    - settings
        - 2D Slider for Pan/Tilt
        - Sliders for other settings
    - save button 
- Fixture Select page with parameter settings
- Groups Seleact page with parameter settings
### fixtures
- can be created from fixture_templates COMP
    - set parameters from fixture_template tableDAT:
    - set settings:
        - Group
        - ID
        - Universe
        - dmx address
        - footprint
    - create master parameters - they work as submasters (not yet used):
        - master dimmer

### post fixture data processing
select specific channel functions from the table process them and inject them back into the network
current features:
- Grandmaster
- 16-bit to 2x8-bit channels
    - mark coarse and fine value in fixture template tables for 16 bit fixtures e.g. Pan Coarse and Pan Fine Channels

### dmx output
able to output multi-universe channels
prepare the available universes based on the used controllers

