import UserInputNode from './UserInputNode';
import LogicBlockNode from './LogicBlockNode';
import ContextNode from './ContextNode';
import DatabaseNode from './DatabaseNode';
import OutputNode from './OutputNode';
import NotesNode from './NotesNode';

export const nodeTypes = {
  userInput: UserInputNode,
  logicBlock: LogicBlockNode,
  context: ContextNode,
  database: DatabaseNode,
  output: OutputNode,
  notes: NotesNode,
};

export { UserInputNode, LogicBlockNode, ContextNode, DatabaseNode, OutputNode, NotesNode };
