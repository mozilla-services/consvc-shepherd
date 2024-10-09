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
      render={({ field, fieldState: { error } }) => (
        <TextField
          {...field}
          {...props}
          error={!!error}
          helperText={error?.message}
          label={label}
        />
      )}
    />
  );
}
