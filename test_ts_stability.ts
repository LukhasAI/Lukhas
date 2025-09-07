// TypeScript stability test
interface TestInterface {
  name: string;
  value: number;
}

function testFunction(param: TestInterface): string {
  return `${param.name}: ${param.value}`;
}

const testObject: TestInterface = {
  name: "test",
  value: 42,
};

console.log(testFunction(testObject));
