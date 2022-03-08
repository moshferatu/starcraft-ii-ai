from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.ids.unit_typeid import UnitTypeId
from sc2.main import run_game
from sc2.player import Bot, Computer

class StalkerBot(BotAI):
    async def on_step(self, iteration: int):
        print(f'The iteration is {iteration}')

        # Put idle workers to work.
        await self.distribute_workers()

        for gateway in self.structures(UnitTypeId.GATEWAY).ready:
            if self.can_afford(UnitTypeId.STALKER):
                gateway.train(UnitTypeId.STALKER)

        if self.townhalls:
            nexus = self.townhalls.random

            if (self.supply_workers + self.already_pending(UnitTypeId.PROBE)) < (self.townhalls.amount * 19):
                if self.can_afford(UnitTypeId.PROBE):
                    nexus.train(UnitTypeId.PROBE)
            
            if not self.structures(UnitTypeId.PYLON).closer_than(15, nexus) or (not self.supply_left and not self.already_pending(UnitTypeId.PYLON)):
                if self.can_afford(UnitTypeId.PYLON):
                    await self.build(UnitTypeId.PYLON, near=nexus)
            
            if self.structures(UnitTypeId.PYLON).closer_than(15, nexus):
                gateway_pylon = self.structures(UnitTypeId.PYLON).closest_to(nexus)
                if not self.structures(UnitTypeId.GATEWAY).closer_than(15, gateway_pylon) and not self.already_pending(UnitTypeId.GATEWAY):
                    if self.can_afford(UnitTypeId.GATEWAY):
                        await self.build(UnitTypeId.GATEWAY, near=gateway_pylon)

            if not self.structures(UnitTypeId.CYBERNETICSCORE) and not self.already_pending(UnitTypeId.CYBERNETICSCORE):
                if self.can_afford(UnitTypeId.CYBERNETICSCORE):
                    await self.build(UnitTypeId.CYBERNETICSCORE, near=self.structures(UnitTypeId.PYLON).closest_to(nexus))
            
            if self.can_afford(UnitTypeId.ASSIMILATOR):
                vespene_geyser = self.vespene_geyser.closest_to(nexus)
                await self.build(UnitTypeId.ASSIMILATOR, near=vespene_geyser)
        
        stalkers = self.units(UnitTypeId.STALKER).idle
        if stalkers.amount >= 5:
            for stalker in stalkers:
                if self.enemy_units:
                    stalker.attack(self.enemy_units.closest_to(stalker))
                elif self.enemy_structures:
                    stalker.attack(self.enemy_structures.closest_to(stalker))
                else:
                    # TODO: Solve for other bases and stalemates.
                    stalker.attack(self.enemy_start_locations[0])

        if (self.townhalls.ready.amount + self.already_pending(UnitTypeId.NEXUS)) < 3:
            if self.can_afford(UnitTypeId.NEXUS):
                await self.expand_now()

run_game(
    maps.get('2000AtmospheresAIE'),
    [
        Bot(Race.Protoss, StalkerBot()),
        Computer(Race.Terran, Difficulty.Easy)
    ],
    realtime=False
)