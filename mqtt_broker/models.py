from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel


### Backend to Broker ###
class PersonaMovement(BaseModel):
  movement: Tuple[int, int]
  pronunciatio: str
  description: str
  chat: Optional[List[str]] = None


class Meta(BaseModel):
  curr_time: str


class Movements(BaseModel):
  persona: Dict[str, PersonaMovement]
  meta: Meta


class BackendToBrokerMessage(BaseModel):
  step: int
  movements: Movements


### Broker to Robots ###
class Position(BaseModel):
  x: int
  y: int


class RobotCommand(BaseModel):
  robot_id: str
  position: Position


class BrokerToRobotsMessage(BaseModel):
  commands: List[RobotCommand]


### Robots to Broker ###
class RobotEnvironment(BaseModel):
  robot_id: str
  position: Position
  perceived: str


class RobotsToBrokerMessage(BaseModel):
  robots: List[RobotEnvironment]


### Broker to Backend ###
class PersonaEnvironment(BaseModel):
  x: int
  y: int
  perceived: str
  maze: str


class BrokerToBackendMessage(BaseModel):
  environment: Dict[str, PersonaEnvironment]
  step: int
