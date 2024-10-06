import scrapy
import os
from urllib.parse import urljoin
import re

class NoblePlantsSpider(scrapy.Spider):
    name = 'noble_plants'
    start_urls = ['https://nobleapps.noble.org/PlantImageGallery/PlantList.aspx?PlantTypeID=3&IndexType=ScientificName']

    # Create a directory for storing images
    if not os.path.exists('noble_plant_images'):
        os.makedirs('noble_plant_images')

    def parse(self, response):
        # Locate all the <a> tags inside the table and loop through them
        for a_tag in response.xpath("//table//a"):
            species_name = a_tag.xpath("text()").get()

            if species_name:
                species_name = species_name.strip()
                # Replace spaces with underscores for valid file names
                species_name = re.sub(r'\s+', '_', species_name.lower())
                species_url = a_tag.xpath("@href").get()

                # Join relative URLs to make absolute URLs
                full_species_url = urljoin(response.url, species_url)

                # Follow each plant species link and pass species_name to the next callback
                yield response.follow(full_species_url, callback=self.parse_species_page, meta={'species_name': species_name})

    def parse_species_page(self, response):
        species_name = response.meta['species_name']

        # Locate the <img> element and extract the image source
        img_url = response.xpath("//img/@src").get()

        if img_url:
            full_img_url = urljoin(response.url, img_url)

            # Create a file name for the image
            image_file_name = f'noble_plant_images/{species_name}.jpg'

            # Download the image
            yield scrapy.Request(full_img_url, callback=self.save_image, meta={'image_file_name': image_file_name})

    def save_image(self, response):
        # Save the image to a local file
        image_file_name = response.meta['image_file_name']
        with open(image_file_name, 'wb') as f:
            f.write(response.body)
