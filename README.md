# TdLightingdesign-ich-bin-mir-selber-fremd-geworden
creating a lighting environment that is portable and minimalistic yet able to do complex stuff: combines lighting, visuals, TouchOSC interface, managing presets, CHOP DMX

## TODOs urgent   
- patch next show
    - reuse backlighting settings from previous show
- test save function (hog CHOP)
- create OSC feedback for:
    - save function
    - fog maching lock



## TODOs
- collect example photos for "fremd geworden" scenes
- UI for setting up parameters:
    - Moving Heads
- presets and groups
    - fixture selector
    - grouping fixtures and controlling them simultaneously
    - presets for Color, Position, FX
- rework TouchOSC patch with grid:text and auto generating and naming faders
- update all UI inputs based on the last one that changed
    - use mapping table
- optimize projector fading from off to on - projector needs a little time to turn on which results in a brightness jump when it turns on 
- UI for OSC Settings with static ip address
- park fixtures
- create a fixture renaming function that also updates the storage table
- create overview plan from network in README.md
- rework network to select visuals - create a projector fixture but don't send it to the dmx channels but it should still populate into the UI
- optimize save function to only store/update changed values to change processing time

## Documentation
### TD Lighting UI
- Master Fader
    - lets you fade between banks with preloaded scenes
- Dimmer page
    - radio buttons for selecting scenes in two preload banks
    - auto-populates dimmer faders based on how many fixtures with dimmers there are
- Save page (yet to be developed)
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