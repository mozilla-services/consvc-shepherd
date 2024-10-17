import "@testing-library/jest-dom";
import { render, screen, fireEvent } from "@testing-library/react";
import { useForm, FormProvider } from "react-hook-form";
import TextInput from "./TextInput";
import PropTypes from "prop-types";

interface TestComponentProps {
  name: string;
  label: string;
  defaultValue?: string;
}

const TestComponent: React.FC<TestComponentProps> = ({
  name,
  label,
  defaultValue,
}) => {
  const methods = useForm({
    defaultValues: {
      [name]: defaultValue,
    },
  });

  return (
    <FormProvider {...methods}>
      <TextInput name={name} label={label} control={methods.control} />
    </FormProvider>
  );
};

TestComponent.propTypes = {
  name: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  defaultValue: PropTypes.string,
};

describe("<TextInput />", () => {
  const setup = (
    name = "testInput",
    label = "Test Input",
    defaultValue = ""
  ) => {
    render(
      <TestComponent name={name} label={label} defaultValue={defaultValue} />
    );
  };

  test("renders the TextInput component with the correct label", () => {
    setup();
    expect(screen.getByLabelText(/test input/i)).toBeInTheDocument();
  });

  test("captures input changes", () => {
    setup();
    const input = screen.getByLabelText(/test input/i);

    fireEvent.change(input, { target: { value: "Hello World" } });
    expect(input.value).toBe("Hello World");
  });
});
