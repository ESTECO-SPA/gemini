from typing import Tuple, List

from scenariogeneration import xosc, Scenario

from external import UdpSender
from gemini.actors import Agent, AgentConnector, UdpSenderXYH
from gemini.action_logic import FollowTrajectoryLogic
from gemini.common import VehicleTrajectory
from gemini.resources import get_resources


def generate_udp_controller(port_number):
    controller = xosc.CatalogReference("ControllerCatalog", "UDPDriverController")
    controller.add_parameter_assignment("Port", port_number)
    controller.add_parameter_assignment("ExecMode", "synchronous")
    return controller


class ScenarioModelObject:

    def __init__(self, agent_id: int, name: str, trajectory: VehicleTrajectory, port_number: int) -> None:
        self.agent_id = agent_id
        self.name = name
        self.initial_state = trajectory.vehicle_states[0]
        self.trajectory = trajectory
        self.port_number = port_number

    def get_agent_id(self) -> int:
        return self.agent_id

    def get_name(self) -> str:
        return self.name

    def get_initial_state(self) -> Tuple[float, float]:
        return self.initial_state.position.x, self.initial_state.position.y

    def get_trajectory(self) -> VehicleTrajectory:
        return self.trajectory

    def get_port_number(self) -> int:
        return self.port_number

    def get_last_time(self):
        return self.trajectory.times[-1]


class ScenarioModelGenerator:

    def __init__(self, target: ScenarioModelObject, obstacles: List[ScenarioModelObject] = None) -> None:
        if obstacles is None:
            obstacles = []
        self.target = target
        self.obstacles = obstacles

    def build_scenario(self) -> Scenario:
        road = xosc.RoadNetwork(scenegraph=get_resources("models", "parking_lot.osgb"))
        catalog = xosc.Catalog()
        catalog.add_catalog('VehicleCatalog',
                            get_resources("xosc", "Catalogs", "Vehicles"))
        catalog.add_catalog('ControllerCatalog',
                            get_resources("xosc", "Catalogs", "Controllers"))

        entities = xosc.Entities()
        entities.add_scenario_object(self.target.get_name(), xosc.CatalogReference('VehicleCatalog', 'car_white'),
                                     generate_udp_controller("53901"))
        init = xosc.Init()
        for obstacle in self.obstacles:
            obstacle_name = obstacle.get_name()
            entities.add_scenario_object(obstacle_name, xosc.CatalogReference('VehicleCatalog', 'car_red'),
                                         generate_udp_controller(str(obstacle.get_port_number())))
            x, y = obstacle.get_initial_state()
            init.add_init_action(obstacle_name, xosc.TeleportAction(xosc.WorldPosition(x, y)))
            init.add_init_action(obstacle_name, xosc.ActivateControllerAction(True, True))
        x, y = self.target.get_initial_state()
        init.add_init_action(self.target.get_name(), xosc.TeleportAction(xosc.WorldPosition(x, y)))
        init.add_init_action(self.target.get_name(), xosc.ActivateControllerAction(True, True))
        board = xosc.StoryBoard(init)
        sce = xosc.Scenario('my first scenario', 'Mandolin', xosc.ParameterDeclarations(), entities=entities,
                            storyboard=board,
                            roadnetwork=road, catalog=catalog)

        return sce

    def get_agent_with_model(self, model_logic):
        actors = list()
        sender = UdpSender(port=self.target.get_port_number())
        actors.append(Agent(action_logic=model_logic,
                            agent_connector=AgentConnector(agent_id=self.target.get_agent_id(),
                                                           osi_channel=UdpSenderXYH(sender))))
        for obstacle in self.obstacles:
            udp_sender = UdpSender(port=obstacle.get_port_number())
            actors.append(Agent(action_logic=FollowTrajectoryLogic(obstacle.get_trajectory()),
                                agent_connector=AgentConnector(agent_id=obstacle.get_agent_id(),
                                                               osi_channel=UdpSenderXYH(udp_sender))))
        return actors

    def get_agents(self):
        actors = list()
        sender = UdpSender(port=53901)
        actors.append(Agent(action_logic=FollowTrajectoryLogic(self.target.get_trajectory()),
                            agent_connector=AgentConnector(agent_id=0,
                                                           osi_channel=UdpSenderXYH(sender))))
        for obstacle in self.obstacles:
            udp_sender = UdpSender(port=obstacle.get_port_number())
            actors.append(Agent(action_logic=FollowTrajectoryLogic(obstacle.get_trajectory()),
                                agent_connector=AgentConnector(agent_id=obstacle.get_agent_id(),
                                                               osi_channel=UdpSenderXYH(udp_sender))))
        return actors

    def get_time(self):
        return self.target.get_last_time()


class ScenarioAgent:
    def __init__(self) -> None:
        self.target = None
        self.interactions = None

    def get_target_info(self, trajectory, port):
        return
