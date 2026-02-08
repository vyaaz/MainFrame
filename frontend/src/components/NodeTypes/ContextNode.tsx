import CustomNode from './CustomNode';

export default function ContextNode(props: any) {
  return <CustomNode {...props} type="context" />;
}
