import { Controller, Control, FieldValues } from "react-hook-form";
import {
  FormControl,
  InputLabel,
  Autocomplete,
  TextField,
  FormHelperText,
} from "@mui/material";

interface SelectInputProps extends FieldValues {
  name: string;
  label: string;
  control: Control;
  options?: { value: string | number; label: string }[];
}

interface Option {
  label: string;
  value: string | number;
}

export default function SelectInput({
  name,
  label,
  control,
  options = [],
}: SelectInputProps) {
  return (
    <Controller
      name={name}
      control={control}
      render={({
        field: { onChange, onBlur, value, ref },
        fieldState: { error },
      }) => (
        <FormControl fullWidth error={!!error}>
          <InputLabel shrink>{label}</InputLabel>
          <Autocomplete
            options={options}
            getOptionLabel={(option: Option) => option.label}
            isOptionEqualToValue={(option: Option, value: Option | null) =>
              option.value === (value ? value.value : "")
            }
            onChange={(_, newValue) => {
              onChange(newValue ? newValue.value : "");
            }}
            onBlur={onBlur}
            value={options.find((option) => option.value === value) ?? null}
            renderInput={(params) => (
              <TextField
                {...params}
                inputRef={ref}
                label={label}
                error={!!error}
              />
            )}
          />
          {error?.message && <FormHelperText>{error.message}</FormHelperText>}
        </FormControl>
      )}
    />
  );
}
