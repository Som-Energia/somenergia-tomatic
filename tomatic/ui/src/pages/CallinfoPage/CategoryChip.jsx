import Chip from '@mui/material/Chip'

export default function CategoryChip({ category, ...props }) {
  return <Chip
    {...props}
    sx={{
      ...props.sx,
      bgcolor: category.color,
      color: (theme) =>
        category.color && theme.palette.getContrastText(category.color),
      '.MuiChip-deleteIcon': {
        color: (theme) =>
          category.color && theme.palette.getContrastText(category.color),
        opacity: 0.9,
      },
    }}
    label={category.name}
  />
}

