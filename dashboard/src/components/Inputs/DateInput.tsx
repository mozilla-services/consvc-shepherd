import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import { Control, Controller } from "react-hook-form";
import dayjs from "dayjs";
import { styled } from "@mui/system";

interface DateInputProps {
  control: Control<any>;
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
      name={name}
      control={control}
      render={({ field: { onChange, value, ref }, fieldState: { error } }) => (
        <LocalizationProvider dateAdapter={AdapterDayjs}>
          <StyledDatePicker
            label={label}
            value={value ? dayjs(value, format) : null}
            onChange={(date) => {
              onChange(date ? dayjs(date).format(format) : null);
            }}
            views={["year", "month", "day"]}
            format={format}
            slotProps={{
              textField: {
                error: !!error,
                helperText: error?.message ? String(error.message) : undefined,
                inputRef: ref,
              },
            }}
          />
        </LocalizationProvider>
      )}
    />
  );
}
