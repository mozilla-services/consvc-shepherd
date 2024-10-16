import "@testing-library/jest-dom";
import { render, screen } from "@testing-library/react";
import { useForm, FormProvider } from "react-hook-form";
import SelectInput from "./SelectInput";
import PropTypes from "prop-types";

interface Option {
  value: string;
  label: string;
}

interface TestComponentProps {
  options: Option[];
}

const TestComponent: React.FC<TestComponentProps> = ({ options }) => {
  const methods = useForm();
  return (
    <FormProvider {...methods}>
      <SelectInput
        control={methods.control}
        name="testSelect"
        label="Test Select"
        options={options}
      />
    </FormProvider>
  );
};

TestComponent.propTypes = {
  options: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
    })
  ).isRequired,
};

describe("<SelectInput />", () => {
  const setup = (options: Option[]) => {
    render(<TestComponent options={options} />);
  };

  test("renders the SelectInput component with the correct label", () => {
    setup([{ value: "1", label: "Option 1" }]);
    expect(screen.getByLabelText(/test select/i)).toBeInTheDocument();
  });
});
