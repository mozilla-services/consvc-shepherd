import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import { Control, Controller, FieldValues } from "react-hook-form";
import dayjs from "dayjs";
import { styled } from "@mui/system";

interface DateInputProps extends FieldValues {
  control: Control;
  name: string;
  format?: string;
  label: string;
}

const StyledDatePicker = styled(DatePicker)`
  width: 100%;
`;

export default function DateInput({
  control,
  name,
  format = "YYYY-MM-DD",
  label,
}: DateInputProps) {
  return (
    <Controller
      control={control}
      name={name}
      render={({ field: { onChange, value, ref }, fieldState: { error } }) => {
        const parsedValue =
          typeof value === "string" || value instanceof Date
            ? dayjs(value)
            : null;

        return (
          <LocalizationProvider dateAdapter={AdapterDayjs}>
            <StyledDatePicker
              label={label}
              value={parsedValue}
              onChange={(date) => {
                onChange(date ? dayjs(date).format(format) : null);
              }}
              views={["year", "month", "day"]}
              format={format}
              slotProps={{
                textField: {
                  error: !!error,
                  helperText: error?.message
                    ? String(error.message)
                    : undefined,
                  inputRef: ref,
                },
              }}
            />
          </LocalizationProvider>
        );
      }}
    />
  );
}
