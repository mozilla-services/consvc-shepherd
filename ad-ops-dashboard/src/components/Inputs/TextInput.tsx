import { Controller, Control, FieldValues } from "react-hook-form";
import { TextField } from "@mui/material";

interface TextInputProps extends FieldValues {
  name: string;
  label: string;
  control: Control<any>;
}

export default function TextInput({
  name,
  label,
  control,
  ...props
}: TextInputProps) {
  return (
    <Controller
      name={name}
      control={control}
      render={({
        field: { onChange, onBlur, value, ref },
        fieldState: { error },
      }) => (
        <TextField
          onChange={(e) =>
            { onChange(props.type === "number" ? +e.target.value : e.target.value); }
          }
          onBlur={onBlur}
          value={value}
          inputRef={ref}
          fullWidth
          label={label}
          {...props}
          error={!!error}
          helperText={error?.message}
        />
      )}
    />
  );
}
