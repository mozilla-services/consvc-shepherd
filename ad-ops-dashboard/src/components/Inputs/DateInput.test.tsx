import "@testing-library/jest-dom";
import { render, screen } from "@testing-library/react";
import { useForm, FormProvider } from "react-hook-form";
import DateInput from "./DateInput";
import PropTypes from "prop-types";

interface TestComponentProps {
  name: string;
  label: string;
  defaultValue?: string | null;
}

const TestComponent: React.FC<TestComponentProps> = ({
  name,
  label,
  defaultValue,
}) => {
  const methods = useForm({
    defaultValues: {
      [name]: defaultValue ?? null,
    },
  });

  return (
    <FormProvider {...methods}>
      <DateInput name={name} label={label} control={methods.control} />
    </FormProvider>
  );
};

TestComponent.propTypes = {
  name: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  defaultValue: PropTypes.string,
};

describe("<DateInput />", () => {
  const setup = (
    name = "testDate",
    label = "Test Date",
    defaultValue = null
  ) => {
    render(
      <TestComponent name={name} label={label} defaultValue={defaultValue} />
    );
  };

  test("renders the DateInput component with the correct label", () => {
    setup();
    expect(screen.getByLabelText(/test date/i)).toBeInTheDocument();
  });
});
