import CustomNode from './CustomNode';

export default function OutputNode(props: any) {
  return <CustomNode {...props} type="output" />;
}
