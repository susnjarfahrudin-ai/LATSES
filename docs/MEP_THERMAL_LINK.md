# MEP Thermal Link

The canonical `HeatingZone.room_id` is the only identity used to connect MEP heating demand to the Thermal room result.

Flow:

`BuildingModel.Room -> Thermal room heat loss -> HeatingZone.room_heat_load_w`

Missing thermal inputs remain `INPUT_REQUIRED`. No second Room or heating model is created.
